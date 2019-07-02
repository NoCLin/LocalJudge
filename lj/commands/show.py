# -*-coding:utf-8-*-
from pathlib import Path

from lj.utils import get_data_dir, get_cases, read_file


def lj_show(args):
    src = Path(args.src)

    data_dir = get_data_dir(src)
    cases = get_cases(data_dir)

    print("case count:%d", len(cases))
    readme_file = data_dir / "README.md"
    if readme_file.exists():
        print(read_file(readme_file))
    else:
        print("no readme!")
    for case in cases:
        stdin = read_file(str(data_dir / (case + ".in")), "r")
        expected_out = read_file(str(data_dir / (case + ".out")), "r")

        print("-> case [%s]" % case)
        print("   stdin:\n" +
              "   " + stdin)
        print("   expected out:\n" +
              "   " + expected_out)
