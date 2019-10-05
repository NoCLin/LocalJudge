# -*-coding:utf-8-*-
import json
import logging

from sys import exit
from pathlib import Path

import argparse
import colorful
from prettytable import PrettyTable

from lj.judger import JudgeStatus
from lj.utils import obj_json_dumps
from lj.vendors.simplediff import diff
from lj.commands.clean import lj_clean
from lj.commands.create import lj_create
from lj.commands.judge import lj_judge
from lj.commands.show import lj_show
from lj.commands.run import lj_compile_and_run

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                    )

# TODO: write log file

logger = logging.getLogger()


def explain_result(result):
    if result.compile.code is not None and result.compile.code != 0:
        print(colorful.red("Compile Error"))
        print(obj_json_dumps(result.compile, indent=2))
        exit()

    status_count = {
        "All": 0,
        JudgeStatus.AC: 0,

    }
    time_col_name = "Time" + \
                    (" < " + "{c.bold}{c.brown}{time}{c.reset}".format(time=result.time_limit, c=colorful)
                     if result.time_limit is not None else "")
    memory_col_name = "Memory" + \
                      (" < " + "{c.bold}{c.brown}{time}{c.reset}".format(time=result.memory_limit, c=colorful)
                       if result.memory_limit is not None else "")

    table = PrettyTable(["Case",
                         "Status",
                         time_col_name,
                         memory_col_name])

    for case in result.cases:
        color_func = colorful.green \
            if case.status == JudgeStatus.AC else colorful.red

        status_count.setdefault(case.status, 0)
        status_count[case.status] += 1
        status_count["All"] += 1

        table.add_row([
            case.case_index,
            '{c.bold}{color_func}{status}{c.reset}'.format(
                status=case.status,
                c=colorful,
                color_func=color_func),
            "%dms" % case.time_used,  # TODO: color
            "%dMB" % case.memory_used,

        ])

    print(table)
    print("=====Summary=====")
    ac_ratio = (status_count[JudgeStatus.AC] / status_count["All"]) * 100

    for status, count in status_count.items():
        if status == JudgeStatus.AC or (status == "All" and ac_ratio == 100):
            status_color_func = colorful.green
        else:
            status_color_func = colorful.red
        print('{c.bold}{status_color_func}{status}{c.reset} {count} {ratio_color_func}{ratio_str}{c.reset}'.format(
            status=status,
            c=colorful,
            status_color_func=status_color_func,
            count=count,
            ratio_color_func=colorful.green if ac_ratio == 100 else colorful.red,
            ratio_str="(%f%%)" % ac_ratio if status == JudgeStatus.AC else ""))

    for case in result.cases:
        if case.status in [JudgeStatus.WA, JudgeStatus.PE]:
            print(colorful.red("-> case [%s] <- %s "
                               % (case.case_index, case.status)))
            print("stdin:")
            print(case.input)
            colored_diff_str = ""

            # TODO: 用网页显示diff，开临时http server 当页面加载完毕时 关闭

            for c in diff(case.expected_output, case.output):
                char = c[1]
                if c[0] == "-":
                    char = "{c.bold_green}" + char + "{c.reset}"
                elif c[0] == "+":
                    char = "{c.bold_red}" + char + "{c.reset}"
                colored_diff_str += char

            x = PrettyTable(["Expected", "Yours"])
            x.add_row([case.expected_output, case.output])
            print(x)
            print("diff:")
            print(colored_diff_str.format(c=colorful))


def main():
    parser = argparse.ArgumentParser(description="Local Judge")
    parser.add_argument("src", help="source file or sub-command")
    parser.add_argument('src2', nargs='?', default="", help="source file for sub-command")
    parser.add_argument("-c", "--case", help="index of test case")
    parser.add_argument("-t", "--time_limit", type=int, default=None, help="time limit (ms)")
    parser.add_argument("-m", "--memory_limit", type=int, default=None, help="memory limit (MB)")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="debug mode")
    parser.add_argument("--json", dest="json", action="store_true", help="output as json")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug("args: %s" % args)

    sub_command_mapping = {
        "clean": lj_clean,
        "create": lj_create,
        "show": lj_show,
        "run": lj_compile_and_run
    }

    # 尝试获取文件，可忽略后缀
    def get_file(file, not_exists_ok=False):
        if file.is_dir():
            # 自动搜索后缀
            file_list = [i for i in file.parent.glob(file.stem + ".*")]
            if len(file_list):
                return file_list[0]
            else:
                print("自动识别后缀失败，文件不存在")
                exit()
        if not_exists_ok is False and not file.is_file():
            print("file does not exist.")
            exit(-1)
        return file

    # 子命令支持
    sub_func = sub_command_mapping.get(args.src)
    if sub_func:
        if not args.src2:
            print("invalid args")
            exit()

        args.command = args.src
        args.src = get_file(Path(args.src2), not_exists_ok=args.command == "create")
        logger.debug("sub_command " + args.command)
        logger.debug(args)
        sub_func(args)
        exit()

    args.src = get_file(Path(args.src), not_exists_ok=False)

    judge_result = lj_judge(args)

    # TODO: ignore any console output
    if args.json:
        print(obj_json_dumps(judge_result, indent=2))
        exit()
    else:
        explain_result(judge_result)


if __name__ == "__main__":
    main()
