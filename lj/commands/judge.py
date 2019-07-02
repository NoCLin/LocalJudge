# -*-coding:utf-8-*-
import logging

from lj.judger import do_judge_run, do_compile, JudgeResultSet
from lj.utils import (
    get_data_dir,
    get_cases,
    read_file
)

logger = logging.getLogger()


# TODO: 支持带空格的文件名？
# TODO: 删除二进制文件
def lj_judge(args):
    src = args.src
    data_dir = get_data_dir(src)
    case_index = args.case

    # time_limit = args.time_limit
    # memory_limit = args.memory_limit

    result = JudgeResultSet()
    result.time_limit = None
    result.memory_limit = None  # TODO: in code (regex)
    result.compile = do_compile(src)

    if result.compile.code is not None and result.compile.code != 0:
        return result

    # TODO: memory limit
    # TODO: output limit

    cases = get_cases(data_dir) if case_index is None else [case_index]
    logger.debug("cases (%d): %s" % (len(cases), cases))

    for case in cases:
        stdin = read_file(str(data_dir / (case + ".in")), "r")
        expected_out = read_file(str(data_dir / (case + ".out")), "r")

        # 支持配配置文件指定限制
        case_result = do_judge_run(command=result.compile.runnable,
                                   stdin=stdin,
                                   expected_out=expected_out,
                                   time_limit=None,
                                   memory_limit=None,
                                   case_index=case
                                   )

        result.cases.append(case_result)

    dest_file = result.compile.params.get("dest")
    if dest_file:
        logger.debug("delete " + dest_file)
    # TODO: delete temp exe
    return result


if __name__ == '__main__':
    pass
