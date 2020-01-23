# -*-coding:utf-8-*-


import json
import logging
import os
import shlex
import subprocess
import tempfile
import threading
import traceback
from pathlib import Path
from string import Template

import psutil

from lj.common import (get_now_ms,
                       print_and_exit,
                       equals_ignore_presentation_error,
                       ignore_last_newline,
                       IS_WINDOWS, read_file, get_memory_by_psutil, shorten_str, get_temp_dir)

logger = logging.getLogger("lj")

DEFAULT_STDOUT_LIMIT = 1024 * 1024 * 32


class JudgeStatus:
    AC = "Accepted"
    WA = "Wrong Answer"
    TLE = "Time Limit Exceeded"
    MLE = "Memory Limit Exceeded"
    OLE = "Output Limit Exceeded"
    PE = "Presentation Error"
    RE = "Runtime Error"
    CE = "Compile Error"


class CompileResult:
    def __init__(self):
        self.command = None
        self.code = None
        self.stdout = None
        self.params = None
        self.runnable = None


class JudgeResultSet:
    def __init__(self):
        self.compile = None
        self.cases = []
        self.time_limit = None
        self.memory_limit = None


class JudgeResult:
    def __init__(self):
        self.case_index = None
        self.command = None
        self.time_limit = None
        self.memory_limit = None
        self.output_limit = None

        self.status = None
        self.code = None
        self.input = None
        self.output = None
        self.expected_output = None

        self.time_used = None
        self.memory_used = None
        self.output_len = None


def load_options():
    file = Path.home() / ".localjudge.json"
    if file.exists():
        try:
            return json.loads(read_file(str(file.resolve()), "r"))
        except json.JSONDecodeError:
            print(str(file) + " parse failed.")
            exit()

    else:
        logger.debug("config file not found!")
        default_config_file = str(Path(__file__).parent / "default.localjudge.json")
        default_options = json.loads(read_file(default_config_file, "r"))
        # path.resolve() will raise FileNotFoundError on Py 3.5.7 if file doesn't exist.
        with open(os.path.abspath(str(file)), "w") as f:
            json.dump(default_options, f, indent=4, ensure_ascii=False)
        return default_options


def get_lang_options_from_suffix(suffix):
    options = load_options()
    try:
        return [lang for lang in options if suffix in lang.get("extensions", [])][0]
    except IndexError:
        print("unsupported suffix: " + suffix)
        exit()


def do_compile(src, additional_compile_flags=None) -> (int, str):
    src_path = Path(src).resolve()
    temp_dir = get_temp_dir(src_path)
    lang_options = get_lang_options_from_suffix(src_path.suffix)
    logger.debug("language options:")
    logger.debug(lang_options)

    compile_result = CompileResult()
    tpl_compile = lang_options.get("compile")
    if additional_compile_flags:
        tpl_compile += " " + additional_compile_flags

    tpl_runnable = lang_options.get("run")
    tpl_dest = lang_options.get("dest")

    params = {
        "src": str(src_path),
        "temp_dir": str(temp_dir),
        "stem": src_path.stem,
        "dest": None,
        "flag_win": "-D_WINDOWS" if IS_WINDOWS else "",
        "exe_if_win": ".exe" if IS_WINDOWS else ""
    }
    # 此时文件还不存在，不要使用pathlib
    params["dest"] = os.path.abspath(str(temp_dir / Template(tpl_dest).substitute(params)))

    if tpl_compile:
        compile_cmd = Template(tpl_compile).substitute(params)

        logger.debug("compile command: %s" % compile_cmd)
        code, stdout = subprocess.getstatusoutput(compile_cmd)
        logger.debug("compile result: code=%d %s" % (code, stdout))
        compile_result.command = compile_cmd
        compile_result.stdout = stdout
        compile_result.code = code

    compile_result.temp_dir = str(temp_dir.resolve())
    compile_result.runnable = Template(tpl_runnable).substitute(params)
    compile_result.params = params

    return compile_result


def do_judge_run(command, stdin="", expected_out="", time_limit=None, memory_limit=None,
                 case_index=None):
    logger.debug("run command: %s" % command)
    logger.debug("stdin: %s" % shorten_str(stdin))
    logger.debug("expected_out: %s" % shorten_str(expected_out))
    logger.debug("time limit: %s" % time_limit)
    logger.debug("memory limit: %s" % memory_limit)

    result = JudgeResult()
    result.command = command
    result.code = None
    result.input = stdin
    result.output = ""
    result.expected_output = expected_out
    result.time_limit = time_limit
    result.memory_limit = memory_limit
    result.case_index = case_index

    # Linux preexec_fn / ulimit
    # MacOS polling psutil
    # Windows winc --memory or polling psutil

    # resource.setrlimit()
    # https://stackoverflow.com/questions/12965023/python-subprocess-popen-communicate-equivalent-to-popen-stdout-read?r=SearchResults

    stdout_fp = tempfile.NamedTemporaryFile("w+", encoding="utf-8")
    p = subprocess.Popen(shlex.split(command, posix=not IS_WINDOWS), shell=False,
                         universal_newlines=True,
                         stdin=subprocess.PIPE,
                         stdout=stdout_fp,
                         stderr=subprocess.STDOUT,
                         )

    # TODO: ole check
    tle_kill = ole_kill = mle_kill = False
    mle_check = True

    max_memory_used = 0

    def memory_monitor():

        nonlocal p, max_memory_used, mle_kill
        try:
            psp = psutil.Process(pid=p.pid)
            while mle_check:
                mem = get_memory_by_psutil(psp)
                # mem = get_memory_by_ps(p.pid) * 1024

                if mem > max_memory_used:
                    logger.debug("polling memory of (%s): %s bytes" % (p.pid, mem))

                    max_memory_used = mem
                    if memory_limit and max_memory_used > memory_limit:
                        logger.debug("reach limit %s %s" % (max_memory_used, memory_limit))
                        mle_kill = True
                        p.kill()
        except Exception as e:
            logger.debug("get memory failed")
            logger.debug(e)

    def output_monitor():
        pass

    mle_check_thread = threading.Thread(target=memory_monitor, args=())
    mle_check_thread.start()

    t2 = get_now_ms()

    try:
        _, _ = p.communicate(stdin,
                             timeout=time_limit / 1000.0 if time_limit else None
                             )
        stdout_fp.seek(0)
        result.output = stdout_fp.read()
    except subprocess.TimeoutExpired:
        p.kill()
        p.kill()
        tle_kill = True
    except Exception as e:
        p.kill()
        logger.error(e)
        traceback.print_exc()

        print_and_exit(-1, "System Error. Please submit an issue.")
    finally:
        stdout_fp.close()
        mle_check = False

    result.code = p.poll()

    t3 = get_now_ms()
    logger.debug("t3: %d t3-t2: %d" % (t3, t3 - t2))
    logger.debug("stdout: %s" % shorten_str(result.output))
    logger.debug("code: %s" % result.code)

    result.time_used = t3 - t2
    result.memory_used = max_memory_used
    result.output_len = len(result.output)

    if tle_kill:  # 超时kill code 非0 必须在判RE前返回
        result.status = JudgeStatus.TLE
        return result

    if mle_kill:
        result.status = JudgeStatus.MLE
        return result

    if ole_kill:
        result.status = JudgeStatus.OLE
        return result

    if result.code != 0:
        result.status = JudgeStatus.RE
        return result

    if result.time_limit is not None \
            and result.time_used > time_limit:
        result.status = JudgeStatus.TLE
        return result

    out = ignore_last_newline(result.output)
    exp = ignore_last_newline(result.expected_output)
    if out == exp:
        result.status = JudgeStatus.AC
        return result

    if equals_ignore_presentation_error(out, exp):
        result.status = JudgeStatus.PE
        return result

    result.status = JudgeStatus.WA
    return result
