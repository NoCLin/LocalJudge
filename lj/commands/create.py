# -*-coding:utf-8-*-

from pathlib import Path
from sys import exit

from lj.common import get_data_dir


def touch_not_exists_and_print(path):
    if path.exists():
        print("file %s already exists." % path.resolve())
        exit()
    path.touch()
    print("create file %s" % path.resolve())


# noinspection PyUnusedLocal
def lj_create(self, src):
    """
    create initial project files.
    :param self:
    :param src:
    :return:
    """
    src_path = Path(src)
    suffix = str(src_path.suffix)

    if not suffix:
        print("invalid suffix")
        exit()

    touch_not_exists_and_print(src_path)

    data_dir = get_data_dir(src_path)
    data_dir.mkdir(parents=True)

    touch_list = ["1.in", "2.in", "1.out", "2.out", "README.md"]
    for file in touch_list:
        touch_not_exists_and_print(data_dir / file)
