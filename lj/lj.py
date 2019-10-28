# -*-coding:utf-8-*-

import logging
import sys
from pathlib import Path
import argparse

from lj.commands.clean import lj_clean
from lj.commands.create import lj_create
from lj.commands.judge import lj_judge
from lj.commands.show import lj_show
from lj.commands.run import lj_compile_and_run
from lj.utils import print_and_exit, get_temp_dir

log_format = '%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s'
logging.basicConfig(handlers=[])
logger = logging.getLogger("lj")
logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Local Judge")
    parser.add_argument("command", nargs="?", default="judge", help="command")
    parser.add_argument('src', help="source file")
    parser.add_argument("-c", "--case", help="index of test case")
    # 指定stdio文件，避免测试时新建重复文件，必须同时存在
    parser.add_argument("-i", "--in_file", help="in file", )
    parser.add_argument("-eo", "--eout_file", help="expected_out file")

    parser.add_argument("-t", "--time_limit", type=int, default=None, help="time limit (ms)")
    parser.add_argument("-m", "--memory_limit", type=int, default=None, help="memory limit (MB)")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="debug mode")
    parser.add_argument("--json", dest="json", action="store_true", help="output as json")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(handler)
        logger.debug("raw args: %s" % args)

    # 尝试获取文件，可忽略后缀
    def try_get_file(file, not_exists_ok=False):
        if file.is_dir():
            # 自动搜索后缀，忽略 .class 等非源文件
            file_list = [i for i in file.parent.glob(file.stem + ".*") if i.suffix not in [".class", ".exe", ".pyc"]]
            if len(file_list):
                return file_list[0]
            else:
                print_and_exit(-1, "自动识别后缀失败，文件不存在")
        if not_exists_ok is False and not file.is_file():
            print_and_exit(-1, "file does not exist.")
        return file

    # 子命令支持
    sub_func = {
        "judge": lj_judge,
        "clean": lj_clean,
        "create": lj_create,
        "show": lj_show,
        "run": lj_compile_and_run
    }.get(args.command, None)

    if not sub_func:
        print_and_exit(-1, 'sub command %s is invalid.' % args.command)

    args.src = try_get_file(Path(args.src), not_exists_ok=args.command == "create")

    tmp_dir = get_temp_dir(args.src)
    logger.debug(Path(args.src).stem)
    log_file = tmp_dir / ("%s.log" % Path(args.src).stem)

    log_file_handler = logging.FileHandler(str(log_file))
    log_file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(log_file_handler)
    logger.debug("logging path: %s" % log_file)
    logger.debug("args: %s" % args)
    sub_func(args)


if __name__ == "__main__":
    main()
