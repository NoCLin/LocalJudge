# -*-coding:utf-8-*-

import datetime
import json
import logging
import platform
import shutil
import sys
from pathlib import Path
from string import Template
import subprocess
import argparse
import colorful
from lj.utils import get_now_ms

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.NOTSET)
fmt = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s]: %(message)s")
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


def compile_source(src_file: str, temp_exe, command) -> (int, str):
    src_file = Path(src_file).resolve()
    command = Template(command).substitute(
        src=src_file.resolve(),
        temp_exe=temp_exe)
    code, out = subprocess.getstatusoutput(command)
    logger.debug("compile command: %s" % command)
    logger.debug("compile result: code=%d %s" % (code, out))
    return code, out


def judge_run(exe_path=None, stdin=None, expected_out=None):
    t1 = get_now_ms()
    ps = subprocess.Popen(exe_path,
                          shell=False,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    logger.debug("exe path: %s" % exe_path)
    logger.debug("stdin: %s" % stdin)
    logger.debug("expected_out: %s" % expected_out)

    stdout, _ = ps.communicate(stdin)
    t2 = get_now_ms()
    logger.debug("stdout: %s" % stdout)

    stdout = stdout.decode().rstrip()
    expected_out = expected_out.rstrip()
    if expected_out == stdout:
        return True, stdout, t2 - t1
    else:
        return False, stdout, t2 - t1


def judge(src=None, case_index=None, time_limit=0):
    src_path = Path(src).resolve()
    data_dir = get_data_dir(src)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = data_dir / "temp" / timestamp
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_exe = str(temp_dir / src_path.stem)
    if platform.system() == "Windows":
        temp_exe += ".exe"

    options = load_options()
    lang = None
    if src_path.suffix == ".c":
        lang = "c"
    elif src_path.suffix in [".cpp", ".cc", "cxx"]:
        lang = "c++"

    json_result = {
        "status": "UNKNOWN",
        "compile": {
            "code": 0,
            "errmsg": "",
            "src": str(src_path),
            "dest": temp_exe,
            "command": options[lang]
        },
        "cases": [],
        "time_limit": time_limit,
        "memory_limit": 0,
        "all": 0,
        "ac": 0,
        "wa": 0,
        "tle": 0,
        "mle": 0,
        "ole": 0,
    }

    code, out = compile_source(str(src_path), temp_exe, options[lang])
    json_result["compile"]["code"] = code
    json_result["compile"]["errmsg"] = out
    if code != 0:
        json_result["status"] = "Compile Error"

        print(json.dumps(json_result, indent=4))
        exit(-1)

    ac_count = 0
    wa_count = 0
    tle_count = 0
    # TODO: memory limit
    mle_count = 0
    # TODO: output limit
    ole_count = 0

    # if time_limit != 0:
    #     print("time limit: %d ms" % time_limit)

    cases = []
    if case_index is None:

        cases = map(lambda x: str(x.stem), data_dir.glob("*.in"))
        cases = sorted(cases)
        print("case (%d):" % len(cases), cases)
    else:
        cases.append(case_index)

    case_count = len(cases)
    json_result["all"] = case_count
    for case in cases:
        case_result = {
            "index": case,
            "status": "",
            "time": -1,
            "in": "",
            "out": "",
            "expected": ""
        }
        with open(str(data_dir / (case + ".in")), "rb") as inf, \
                open(str(data_dir / (case + ".out")), "r") as outf:

            stdin = inf.read()
            expected_out = outf.read()
            result, out, ms = judge_run(exe_path=temp_exe,
                                        stdin=stdin,
                                        expected_out=expected_out
                                        )
            case_result["in"] = stdin.decode()
            case_result["out"] = out
            case_result["time"] = ms
            case_result["expected"] = expected_out

            is_timeout = time_limit != 0 and ms >= time_limit
            if is_timeout:
                tle_count += 1
                case_result["status"] = "Timeout"
                print(colorful.red("-> case [%s] <- timeout" % case))
            elif not result:
                case_result["status"] = "Wrong Answer"
                print(colorful.red("-> case [%s] <- wrong answer" % case))
                print("   stdin:\n" +
                      "   " + stdin.decode())
                print("   stdout:\n" +
                      "   " + out)
                print("   expected:\n" +
                      "   " + expected_out)
                wa_count += 1
            else:
                case_result["status"] = "Accepted"
                print(colorful.green("-> case [%s] <- accepted" % case))
                ac_count += 1
            json_result["cases"].append(case_result)
            print("   in %d ms" % ms)
    json_result["ac"] = ac_count
    json_result["wa"] = wa_count
    json_result["tle"] = tle_count
    json_result["mle"] = mle_count
    json_result["ole"] = ole_count
    # TODO: json output
    # print(json.dumps(json_result, indent=4))
    print("=====summary=====")

    print(colorful.red("Wrong Answer: %s" % wa_count),
          colorful.red("Time Limit Exceeded : %s" % tle_count),
          colorful.red("Memory Limit Exceeded : %s" % tle_count)
          )
    print("All: %d" % case_count,
          colorful.green("Accepted: %s (%f %%)" %
                         (ac_count, (ac_count / float(case_count) * 100))))


def get_data_dir(src):
    src_path = Path(src)
    stem = str(src_path.stem)
    return (src_path.parent / stem).resolve()


def load_options():
    options = {
        "c": "gcc ${src} -o ${temp_exe}",
        "c++": "g++ ${src} -o ${temp_exe}"
    }

    # noinspection PyBroadException
    try:
        file = Path.home() / ".localjudge.json"
        with open(str(file.resolve())) as f:
            options = json.load(f)
    except Exception:
        logger.warning("config file not found!")
    return options


def show(src: Path):
    data_dir = get_data_dir(src)

    cases = map(lambda x: str(x.stem), data_dir.glob("*.in"))
    cases = sorted(cases)
    print("case count:", len(cases))
    readme_file = data_dir / "README.md"
    if readme_file.exists():
        with open(readme_file, "r") as f:
            print(f.read())
    else:
        print("no readme!")
    for case in cases:
        with open(str(data_dir / (case + ".in")), "rb") as inf, \
                open(str(data_dir / (case + ".out")), "r") as outf:
            print("-> case [%s]" % case)
            stdin = inf.read()
            expected_out = outf.read()
            print("   stdin:\n" +
                  "   " + stdin.decode())
            print("   expected out:\n" +
                  "   " + expected_out)


def main():
    parser = argparse.ArgumentParser(description="Local Judge")
    parser.add_argument("src",
                        help="source file")
    parser.add_argument("-c",
                        "--case",
                        dest="case",
                        help="index of test case")
    parser.add_argument("-t",
                        "--timelimit",
                        dest="timelimit",
                        type=int,
                        default=0,
                        help="time limit (ms)")

    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="debug mode")
    parser.add_argument("-s", "--show", dest="show", action="store_true",
                        help="show cases")
    parser.add_argument("--clean", dest="clean", action="store_true",
                        help="clean temp")
    # TODO: 输出json数据，便于测试
    parser.add_argument("--json", dest="json", action="store_true",
                        help="show json")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.show:
        print("show")
        show(src=args.src)
        exit()

    if args.clean:
        data_dir = get_data_dir(args.src)
        dir_path = str((data_dir / "temp").resolve())
        print("clean temp dir" + dir_path)
        shutil.rmtree(dir_path)
        exit()

    # judge
    print("judging")

    judge(src=args.src,
          case_index=args.case,
          time_limit=args.timelimit)


if __name__ == "__main__":
    main()
