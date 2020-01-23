# -*-coding:utf-8-*-
import shlex
import subprocess
from pathlib import Path

from lj.common import IS_WINDOWS


# noinspection PyUnusedLocal
def lj_generator_out(self, out_generator_program, name):
    """
    run `out_generator_program` to generator *.out by `name`/*.in
    :param self:
    :param out_generator_program:
    :param name:
    :return:
    """
    for infile in Path(name).glob("*.in"):
        with open(str(infile)) as f:
            stdin = f.read()
            p = subprocess.Popen(shlex.split(out_generator_program, posix=not IS_WINDOWS), shell=False,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)

            stdout, _ = p.communicate(stdin)
            status = p.poll()

            if status != 0:
                print("exec command `%s` got non-zero return value: %d." % (out_generator_program, status))
                return

            outfile = str(infile.parent / ("%s.out" % infile.stem))
            with open(outfile, "w") as fo:
                fo.write(stdout)
            print("%s < %s > %s" % (out_generator_program, infile, outfile))
