# -*-coding:utf-8-*-
import os
import sys
import datetime
import json
import logging
import re
import time
from pathlib import Path

import jsonpickle

logger = logging.getLogger()
IS_WINDOWS = sys.platform == "win32"


# ref: https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
def natural_sort(l):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


def get_data_dir(src) -> Path:
    src_path = Path(src)
    stem = str(src_path.stem)
    return (src_path.parent / stem).resolve()


def get_all_temp_dir(src):
    src_path = Path(src)
    return (src_path.parent / ".local_judge").glob(src_path.stem + "_*")


def get_temp_dir(src) -> Path:
    src_path = Path(src)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = src_path.parent / ".local_judge" / (src_path.stem + "_" + timestamp)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir.resolve()


def load_options():
    logging.debug("loading options")
    file = Path.home() / ".localjudge.json"
    if file.exists():
        try:
            return json.loads(read_file(str(file.resolve()), "r"))
        except json.JSONDecodeError:
            print(str(file) + " parse failed.")
            exit()

    else:
        logger.debug("config file not found!")
        default_config_file = str(Path(__file__).parent / "default.localjudge.json")
        default_options = json.loads(read_file(default_config_file, "r"))
        # path.resolve() will raise FileNotFoundError on Py 3.5.7 if file doesn't exist.
        with open(os.path.abspath(str(file)), "w") as f:
            json.dump(default_options, f, indent=4, ensure_ascii=False)
        return default_options


def get_cases(data_dir):
    cases = map(lambda x: str(x.stem), data_dir.glob("*.in"))
    return natural_sort(cases)


def get_now_ms():
    return (time.clock() if IS_WINDOWS else time.time()) * 1000


def ignore_last_newline(s):
    if s[-1:] == '\n':  # 只移除最后一个\n
        return s[:-1]
    return s


def rstrip_each_line(s):
    return "\n".join([line.rstrip() for line in s.splitlines()])


def equals_ignore_presentation_error(str1, str2):
    return rstrip_each_line(str1) == rstrip_each_line(str2)


def read_file(file, mode='r'):
    with open(file, mode=mode) as f:
        return f.read()


def obj_json_dumps(obj, indent=None):
    r = jsonpickle.encode(obj, unpicklable=False)
    if indent:
        return json.dumps(json.loads(r), indent=indent, ensure_ascii=False)
    return r


def diff_print_colored(source, dest):
    pass
