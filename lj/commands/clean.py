# -*-coding:utf-8-*-
import shutil

from lj.utils import get_all_temp_dir


def lj_clean(args):
    temp_dirs = get_all_temp_dir(args.src)
    for i in temp_dirs:
        print("clean temp dir " + str(i))
        shutil.rmtree(str(i.resolve()))
