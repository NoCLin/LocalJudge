# -*-coding:utf-8-*-
import shutil
from pathlib import Path

from lj.common import TEMP_DIR_NAME


def get_all_temp_dir(src):
    src_path = Path(src)
    return (src_path.parent / TEMP_DIR_NAME).glob(src_path.stem + "_*")


# noinspection PyUnusedLocal
def lj_clean(self, src):
    """
    clean project temp files.
    :param self:
    :param src:
    :return:
    """
    temp_dirs = get_all_temp_dir(src)

    for i in temp_dirs:
        print("clean temp dir " + str(i))
        shutil.rmtree(str(i.resolve()))
