# -*-coding:utf-8-*-
import logging
import shlex
import shutil
import subprocess
import sys

import colorful

from lj.common import obj_json_dumps, IS_WINDOWS, try_get_file, get_temp_dir
from lj.judger import do_compile

logger = logging.getLogger("lj")


# noinspection PyUnusedLocal
def lj_compile_and_run(self, src, additional_compile_flags=""):
    """
    directly compile and run with source file.
    :param self:
    :param src:
    :param additional_compile_flags:
    :return:
    """
    tmp_dir = get_temp_dir(src)

    src = try_get_file(src)
    compile_result = do_compile(src, additional_compile_flags)
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
