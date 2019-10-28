# -*-coding:utf-8-*-
import argparse
import logging
import shlex
import shutil
import subprocess
import sys

from lj.judger import do_compile
from lj.utils import obj_json_dumps, IS_WINDOWS

logger = logging.getLogger("lj")


def lj_compile_and_run(args):
    compile_result = do_compile(args.src)

    if compile_result.code == 0:
        run_with_console(compile_result.runnable)
        shutil.rmtree(compile_result.temp_dir)
        print("Removing " + compile_result.temp_dir)
    else:
        print(obj_json_dumps(compile_result, indent=2))
        print("Compile Error:\n")
        print(compile_result.stdout)


def run_with_console(command):
    print("Running %s" % command)

    proc = subprocess.Popen(shlex.split(command, posix=not IS_WINDOWS), shell=False,
                            stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    print("PID: %d" % proc.pid)
    print("-" * 20)
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
