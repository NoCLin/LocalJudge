# -*-coding:utf-8-*-
import os
import subprocess
import sys


# noinspection PyUnusedLocal
def lj_docker(self):
    """
    enter docker environment.
    :param self:
    :return:
    """
    code_dir = os.getcwd()
    commands = ["docker", "run",
                "-it", "--rm",
                "--volume", "%s:%s" % (code_dir, "/code"),
                "--workdir", "/code",
                "localjudge", 'bash']
    print("calling %s" % commands)
    p = subprocess.Popen(commands, shell=False,
                         stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    try:
        p.communicate()
    except KeyboardInterrupt:
        pass
    print("Bye")
