# -*-coding:utf-8-*-
import copy
import datetime
import json
import logging
import re
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import jsonpickle

from lj.vendors.human_bytes_converter import human2bytes

logger = logging.getLogger("lj")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"
LOG_FORMAT = '%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s'


def print_and_exit(code, text):
    print(text)
    sys.exit(code)


# ref: https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
def natural_sort(l):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


# 尝试获取文件，可忽略后缀
def try_get_file(file, not_exists_ok=False):
    file = Path(str(file))
    if file.is_dir():
        # 自动搜索后缀，忽略 .class 等非源文件
        ignore_extensions = [".class", ".exe", ".pyc"]
        file_list = [i for i in file.parent.glob(file.stem + ".*") if i.suffix not in ignore_extensions]
        if len(file_list):
            return file_list[0]
        else:
            print_and_exit(-1, "自动识别后缀失败，文件不存在")
    if not_exists_ok is False and not file.is_file():
        print_and_exit(-1, "file `%s` does not exist." % file)
    return file


def get_data_dir(src, overwrite=None) -> Path:
    if overwrite:
        return Path(overwrite).resolve()
    src_path = Path(src)
    stem = str(src_path.stem).split("@")[0]
    return (src_path.parent / stem).resolve()


TEMP_DIR_NAME = ".lj"


# NOTE: 每次运行保证相同参数的返回值一致，确保maxsize 足够大，调用次数足够少
@lru_cache(maxsize=10000)
def get_temp_dir(src) -> Path:
    src_path = Path(src)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = src_path.parent / TEMP_DIR_NAME / str(src_path.stem) / timestamp
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir.resolve()


def get_cases(data_dir):
    cases = map(lambda x: str(x.stem), data_dir.glob("*.in"))
    return natural_sort(cases)


def get_now_ms():
    return time.perf_counter() * 1000


# 在部分系统 会多一个"\n"，此处直接删除末尾所有的"\n"
def ignore_last_newline(s):
    return s.rstrip("\n")


def rstrip_each_line(s):
    return "\n".join([line.rstrip() for line in s.splitlines()])


def equals_ignore_presentation_error(str1, str2):
    return rstrip_each_line(str1) == rstrip_each_line(str2)


def read_file(file, mode='r'):
    with open(file, mode=mode) as f:
        return f.read()


def shorten_str(_str, max_len=100):
    return _str[:max_len] + "..." if len(_str) > max_len else _str


def shorten_case(c):
    c.input = shorten_str(c.input)
    c.output = shorten_str(c.output)
    c.expected_output = shorten_str(c.expected_output)
    return c


def shorten_result(result):
    o = copy.deepcopy(result)
    for c in o.cases:
        c = shorten_case(c)
    return o


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
    >>> from os import linesep
    >>> code  = '/**' +  linesep
    >>> code += ' * Time limit: 1000MS'+ linesep
    >>> code += ' * memoryLimit：10000K'+ linesep
    >>> code += '**/'
    >>> get_time_and_memory_limit(code)
    (1000.0, 10240000)
    >>> code  = '#time limit: 1s' + linesep
    >>> code += '#memorylimit: 1m' + linesep
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
    except Exception:
        return 0
