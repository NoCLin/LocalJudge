# -*-coding:utf-8-*-

from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description="Local Judge Creator")
    parser.add_argument("src", help="source file")

    args = parser.parse_args()

    src_path = Path(args.src)
    src_path.touch()

    stem = str(src_path.stem)
    data_dir = src_path.parent / stem

    data_dir.mkdir(parents=True)

    (data_dir / "1.in").touch()
    (data_dir / "1.out").touch()
    (data_dir / "2.in").touch()
    (data_dir / "2.out").touch()
    (data_dir / "README.md").touch()


if __name__ == "__main__":
    main()
