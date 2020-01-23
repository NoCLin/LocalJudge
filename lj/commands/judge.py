# -*-coding:utf-8-*-
import collections
import logging
import os
import sys
import warnings
from pathlib import Path

import colorful

from lj.common import (
    LOG_FORMAT,
    get_data_dir, get_cases, get_temp_dir,
    read_file, try_get_file,
    get_time_and_memory_limit,
    obj_json_dumps, shorten_result, )
from lj.judger import do_judge_run, do_compile, JudgeStatus, JudgeResultSet
from lj.vendors.human_bytes_converter import bytes2human
from lj.vendors.simplediff import diff

logger = logging.getLogger("lj")

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from prettytable import PrettyTable


def explain_result(result, json=False):
    if json:
        print(obj_json_dumps(shorten_result(result), indent=2))
        return
    # TODO: 实时展示judge 结果
    # None 为不需要编译
    if result.compile.code is not None and result.compile.code != 0:
        print(obj_json_dumps(result.compile, indent=2))
        print(colorful.red("Compile Error"))
        print(result.compile.stdout)
        return
    if len(result.cases) == 0:
        print("no cases.")
        return

    time_col_name = "Time"
    if result.time_limit is not None:
        time_col_name += " < " + "{c.bold}{time}ms{c.reset}".format(time=result.time_limit, c=colorful)
    memory_col_name = "Memory"

    # colorful.italics
    if result.memory_limit is not None:
        memory_col_name += " < " + "{c.bold}{memory}{c.reset}".format(
            memory=bytes2human(result.memory_limit),
            c=colorful)

    table = PrettyTable(["Case",
                         "Status",
                         time_col_name,
                         memory_col_name])
    status_count = collections.OrderedDict()
    status_count["All"] = 0
    status_count[JudgeStatus.AC] = 0

    collections.OrderedDict()
    for case in result.cases:
        status_count.setdefault(case.status, 0)
        status_count[case.status] += 1
        status_count["All"] += 1

        table.add_row([
            case.case_index,
            '{c.bold}{color_func}{status}{c.reset}'.format(
                c=colorful, status=case.status,
                color_func=colorful.green if case.status == JudgeStatus.AC else colorful.red),

            "{c.bold}{color_func}{time}ms{c.reset}".format(
                c=colorful,
                color_func=colorful.red if case.status == JudgeStatus.TLE else "",
                time="%.2f" % case.time_used),

            "{c.bold}{color_func}{memory}{c.reset}".format(
                c=colorful,
                color_func=colorful.red if case.status == JudgeStatus.MLE else "",
                memory=bytes2human(case.memory_used)),

        ])

    print(table)
    ac_ratio = (status_count[JudgeStatus.AC] / status_count["All"]) * 100

    for status, count in status_count.items():

        if status == JudgeStatus.AC or (status == "All" and ac_ratio == 100):
            status_color_func = colorful.green
        else:
            status_color_func = colorful.red
        print(
            '{c.bold}{status_color_func}{status}{c.reset} {count} {c.bold}{ratio_color_func}{ratio_str}{c.reset}'.format(
                c=colorful,
                status_color_func=status_color_func,
                ratio_color_func=colorful.green if ac_ratio == 100 else colorful.red,
                status=status,
                count=count,
                ratio_str="(%.2f%%)" % ac_ratio if status == JudgeStatus.AC else ""))
    print()

    for case in result.cases:
        if case.status in [JudgeStatus.WA, JudgeStatus.PE]:
            print('{c.bold}{c.red}-> case [{index}] <- {status} {c.reset}{c.bold}'
                  .format(c=colorful,
                          index=case.case_index,
                          status=case.status))
            # FIXME: shorten
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


# noinspection PyUnusedLocal
def lj_judge(self,
             src,
             case_index=None,
             json=False,
             time_limit=None,
             memory_limit=None,
             data_dir=None):
    """
    local judge source file.
    :param self:
    :param src:
    :param case_index:
    :param json:
    :param time_limit:
    :param memory_limit:
    :param data_dir:
    :return:
    """

    tmp_dir = get_temp_dir(src)
    logger.debug("Temp Dir is %s, exists: %s " % (tmp_dir, tmp_dir.exists()))

    log_file = os.path.join(str(tmp_dir), "lj.log")
    logger.debug("logging path: %s" % log_file)

    log_file_handler = logging.FileHandler(log_file)
    log_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(log_file_handler)

    logger.debug("args: %s" % sys.argv)
    src = try_get_file(Path(src), not_exists_ok=False)
    logger.debug("src is: %s" % src)

    result = JudgeResultSet()
    result.time_limit = None
    result.memory_limit = None
    result.compile = do_compile(src)

    if result.compile.code is not None and result.compile.code != 0:
        explain_result(result, json)
        return

    source_code = read_file(result.compile.params["src"])

    logger.info("source code:\n\n%s\n\n" % source_code)

    tl, ml = (get_time_and_memory_limit(source_code))

    result.time_limit = time_limit if time_limit else tl
    result.memory_limit = memory_limit * 1024 * 1024 if memory_limit else ml

    data_dir = get_data_dir(src, data_dir)
    case_indexes = get_cases(data_dir) if case_index is None else [case_index]
    judge_cases_group = [
        {
            "in": str(data_dir / (i + ".in")),
            "eout": str(data_dir / (i + ".out")),
            "name": i
        } for i in case_indexes
    ]

    logger.debug("cases (%d): %s" % (len(judge_cases_group), judge_cases_group))

    for case in judge_cases_group:
        stdin = read_file(case["in"], "r")
        expected_out = read_file(case["eout"], "r")

        # 支持配配置文件指定限制
        case_result = do_judge_run(command=result.compile.runnable,
                                   stdin=stdin,
                                   expected_out=expected_out,
                                   time_limit=result.time_limit,
                                   memory_limit=result.memory_limit,
                                   case_index=case["name"]
                                   )

        result.cases.append(case_result)

    explain_result(result, json)

    dest_file = result.compile.params.get("dest")
    if dest_file:
        logger.debug("delete " + dest_file)
        try:
            Path(dest_file).unlink()
        except Exception as e:
            logger.error("delete failed.")
            logger.error(e)

    logger.info("result:\n%s" % obj_json_dumps(shorten_result(result), indent=2))


if __name__ == '__main__':
    pass
