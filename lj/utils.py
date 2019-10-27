# -*-coding:utf-8-*-
import os
import subprocess
import sys
import time
import datetime
import json
import logging
import re

from pathlib import Path

import jsonpickle

from lj.vendors.human_bytes_converter import human2bytes

logger = logging.getLogger("lj")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"


def print_and_exit(code, text):
    if hasattr(sys, "stdout_"):
        sys.stdout = sys.stdout_
    print(text)
    sys.exit(code)


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


def bytes_to_string():
    pass


def string_to_ms(size_str):
    """
        >>> string_to_ms("1.1")
        1.1
        >>> string_to_ms("1S")
        1000.0
        >>> string_to_ms("1ms")
        1.0
        >>> string_to_ms("1.1ms")
        1.1
    """

    if size_str[-2:].upper() == "MS":
        return float(size_str[:-2])

    if size_str[-1].upper() == "S":
        return 1000 * float(size_str[:-1])
    return float(size_str)


def get_time_and_memory_limit(source_code):
    """
    :param source_code:
    :return: time_limit(ms) , memory_limit(bytes)

    >>> code  = '/**' +  os.linesep
    >>> code += ' * Time limit: 1000MS'+ os.linesep
    >>> code += ' * memoryLimit：10000K'+ os.linesep
    >>> code += '**/'
    >>> get_time_and_memory_limit(code)
    (1000.0, 10240000)
    >>> code  = '#time limit: 1s'+os.linesep
    >>> code += '#memorylimit: 1m'+os.linesep
    >>> get_time_and_memory_limit(code)
    (1000.0, 1048576)
    """
    search1 = re.search(r'[Tt]ime.?[Ll]imit.?[:：](.*)\n', source_code, re.M)
    tl = None
    ml = None
    if search1:
        tl = search1.group(1).strip()
        tl = string_to_ms(tl)
    search2 = re.search(r'[Mm]emory.?[Ll]imit.?[:：](.*)\n', source_code, re.M)
    if search2:
        ml = search2.group(1).strip()
        ml = human2bytes(ml.upper())
        ml = ml

    return tl, ml


def get_memory_by_ps(pid):
    # windows powershell -Command "Get-Process"
    out = subprocess.getoutput("ps -o rss -p %s" % pid).strip(" RS\n")
    return 0 if out == "" else int(out)


def get_memory_by_psutil(p):
    try:
        return p.memory_info().rss
    except:
        return 0
