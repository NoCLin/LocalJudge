# -*-coding:utf-8-*-
import argparse
import logging
import shutil
import subprocess
import sys

from lj.judger import do_compile

logger = logging.getLogger()


def lj_compile_and_run(args):
    compile_result = do_compile(args.src)

    if compile_result.code == 0:
        run_with_console(compile_result.runnable)
        shutil.rmtree(compile_result.temp_dir)
        print("Removing " + compile_result.temp_dir)


def run_with_console(command):
    print("Running %s" % command)
    print("-" * 20)
    # 如果文件名含有空格，用户必须输入引号
    proc = subprocess.Popen(command.split(), shell=False, stdin=sys.stdin, stdout=sys.stdout)
    try:
        while proc.poll() is None:
            pass
    except KeyboardInterrupt:
        pass

    print()
    print("-" * 20)
    print("Process Exit Code: %s" % (str(proc.returncode)))


def main():
    parser = argparse.ArgumentParser(description="Local Judge Runner")
    parser.add_argument("src", help="source file")
    args = parser.parse_args()
    lj_compile_and_run(args)


if __name__ == "__main__":
    main()
