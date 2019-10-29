# -*-coding:utf-8-*-
import argparse
import logging
import shlex
import shutil
import subprocess
import sys

import colorful

from lj.judger import do_compile
from lj.utils import obj_json_dumps, IS_WINDOWS

logger = logging.getLogger("lj")


def lj_compile_and_run(args):
    compile_result = do_compile(args.src)
    print("compile command: %s" % compile_result.command)
    if compile_result.code == 0:
        run_with_console(compile_result.runnable)
        shutil.rmtree(compile_result.temp_dir)
        print("Removing " + compile_result.temp_dir)
    else:
        print(obj_json_dumps(compile_result, indent=2))
        print(colorful.red("Compile Error"))
        print(compile_result.stdout)


def run_with_console(command):
    print("Running %s" % command)

    p = subprocess.Popen(shlex.split(command, posix=not IS_WINDOWS), shell=False,
                         stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    print("PID: %d" % p.pid)
    print("-" * 20)
    try:
        p.communicate()
    except KeyboardInterrupt:
        pass
    print()
    print("-" * 20)
    print("Process Exit Code: %s" % (str(p.returncode)))


def main():
    parser = argparse.ArgumentParser(description="Local Judge Runner")
    parser.add_argument("src", help="source file")
    args = parser.parse_args()
    lj_compile_and_run(args)


if __name__ == "__main__":
    main()
