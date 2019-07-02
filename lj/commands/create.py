# -*-coding:utf-8-*-

from pathlib import Path
import argparse
from sys import exit

from lj.utils import get_data_dir


def touch_not_exists_and_print(path):
    if path.exists():
        print("file %s already exists." % path.resolve())
        exit()
    path.touch()
    print("create file %s" % path.resolve())


def lj_create(args):
    src_path = Path(args.src)
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


def main():
    parser = argparse.ArgumentParser(description="Local Judge Creator")
    parser.add_argument("src", help="source file")

    args = parser.parse_args()
    lj_create(args)


if __name__ == "__main__":
    main()
