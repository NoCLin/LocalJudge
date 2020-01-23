__VERSION__ = (1, 0, 0)

import logging
import sys

from fire import Fire

from lj.commands.clean import lj_clean
from lj.commands.create import lj_create
from lj.commands.docker import lj_docker
from lj.commands.gin import lj_generator_in
from lj.commands.gout import lj_generator_out
from lj.commands.judge import lj_judge
from lj.commands.run import lj_compile_and_run
from lj.commands.show import lj_show
from lj.common import LOG_FORMAT

logging.basicConfig(handlers=[])
logger = logging.getLogger("lj")
logger.setLevel(logging.INFO)


class LocalJudge:

    def __init__(self, debug=False):
        if debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(handler)
            logger.debug("raw args: %s" % sys.argv)


LocalJudge.judge = lj_judge
LocalJudge.create = lj_create
LocalJudge.show = lj_show
LocalJudge.clean = lj_clean
LocalJudge.docker = lj_docker
LocalJudge.run = lj_compile_and_run
LocalJudge.gin = lj_generator_in
LocalJudge.gout = lj_generator_out


def ljc_main():
    sys.argv.insert(1, "create")
    Fire(LocalJudge)


def ljr_main():
    # 自动省略 run 命令
    sys.argv.insert(1, "run")
    Fire(LocalJudge)


def lj_main():
    # 未输入子命令时 默认为judge
    if len(sys.argv) > 1 and not getattr(LocalJudge, sys.argv[1], None):
        sys.argv.insert(1, "judge")
    Fire(LocalJudge)
