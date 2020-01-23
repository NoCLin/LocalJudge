# -*-coding:utf-8-*-


# noinspection PyUnusedLocal
import os
import subprocess
from pathlib import Path


# noinspection PyUnusedLocal
def lj_generator_in(self, in_generator_program, name, a, b):
    """
    generate data by `in_generator_program`, save case to folder `name` in range(a,b+1).
    :param self:
    :param in_generator_program
    :param name:
    :param a:
    :param b:
    """
    for i in range(a, b + 1):
        base_dir = Path(os.path.curdir) / name
        base_dir.mkdir(exist_ok=True)
        filename = str(base_dir / ("%d.in" % i))
        print("%s > %s" % (in_generator_program, filename))
        status, output = subprocess.getstatusoutput(in_generator_program)
        if status != 0:
            print("exec command `%s` got non-zero return value: %d." % (in_generator_program, status))
            return
        with open(filename, "w") as f:
            f.write(output)
