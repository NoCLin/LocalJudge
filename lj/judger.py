import logging
import os
import platform
import subprocess
from pathlib import Path
from string import Template

from lj.utils import (get_now_ms,
                      equals_ignore_presentation_error,
                      ignore_last_newline,
                      get_temp_dir,
                      load_options)

logger = logging.getLogger()


class JudgeStatus:
    AC = "Accepted"
    WA = "Wrong Answer"
    TLE = "Time Limit Exceeded"
    MLE = "Memory Limit Exceeded"
    OLE = "Output Limit Exceeded"
    PE = "Presentation Error"
    RE = "Runtime Error"
    CE = "Compile Error"


class CompileResult:
    def __init__(self):
        self.command = None
        self.code = None
        self.stdout = None
        self.params = None
        self.runnable = None


class JudgeResultSet:
    def __init__(self):
        self.compile = None
        self.cases = []
        self.time_limit = None
        self.memory_limit = None


class JudgeResult:
    def __init__(self):
        self.case_index = None
        self.command = None
        self.time_limit = None
        self.memory_limit = None
        self.output_limit = None

        self.status = None
        self.code = None
        self.input = None
        self.output = None
        self.expected_output = None

        self.time_used = None
        self.memory_used = None
        self.output_len = None


def get_lang_options_from_suffix(suffix):
    options = load_options()
    try:
        lang_options = [lang for lang in options if suffix in lang.get("extensions", [])][0]
        logging.debug("language options")
        logging.debug(lang_options)
        return lang_options
    except IndexError:
        print("unsupported suffix: " + suffix)
        exit()


def do_compile(src) -> (int, str):
    src_path = Path(src).resolve()
    temp_dir = get_temp_dir(src)
    lang_options = get_lang_options_from_suffix(src_path.suffix)

    compile_result = CompileResult()
    compile_cmd_template = lang_options.get("compile")

    run_cmd_template = lang_options.get("run")
    dest_template = lang_options.get("dest")

    params = {
        "src": str(src_path),
        "stem": src_path.stem,
        "dest": None,
        "exe_if_win": ".exe" if platform.system() == "Windows" else ""
    }
    # 此时文件还不存在
    params["dest"] = os.path.abspath(str(temp_dir / Template(dest_template).substitute(params)))

    if compile_cmd_template:
        compile_cmd = Template(compile_cmd_template).substitute(params)

        logger.debug("compile command: %s" % compile_cmd)
        code, stdout = subprocess.getstatusoutput(compile_cmd)
        logger.debug("compile result: code=%d %s" % (code, stdout))
        compile_result.command = compile_cmd
        compile_result.stdout = stdout
        compile_result.code = code

    compile_result.temp_dir = str(temp_dir.resolve())
    compile_result.runnable = Template(run_cmd_template).substitute(params)
    compile_result.params = params

    return compile_result


def do_judge_run(command, stdin=None, expected_out=None, time_limit=None, memory_limit=None, output_limit=1024,
                 case_index=None):
    logger.debug("run command: %s" % command)
    logger.debug("stdin: %s" % stdin)
    logger.debug("expected_out: %s" % expected_out)

    result = JudgeResult()
    result.command = command
    result.input = stdin
    result.expected_output = expected_out
    result.time_limit = time_limit
    result.memory_limit = memory_limit
    result.case_index = case_index

    t1 = get_now_ms()
    logger.debug("t1: %d" % t1)
    ps = subprocess.Popen(command.split(), shell=False,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    t2 = get_now_ms()
    logger.debug("t2: %d t2-t1: %d" % (t2, t2 - t1))

    # FIXME: 不要直接使用communicate，否则不好处理内存与时间占用
    stdout, _ = ps.communicate(stdin.encode())

    # TODO: 处理 Runtime Error 等

    t3 = get_now_ms()
    logger.debug("t3: %d t3-t2: %d t3-t1: %d" % (t3, t3 - t2, t3 - t1))

    result.time_used = t3 - t1
    result.memory_used = 0
    result.output = stdout.decode()

    result.code = 0
    if result.code != 0:
        result.status = JudgeStatus.RE
        return result

    if result.memory_limit is not None \
            and result.memory_used > memory_limit:
        result.status = JudgeStatus.MLE
        return result

    if result.time_limit is not None \
            and result.time_used > time_limit:
        result.status = JudgeStatus.TLE
        return result

    out = ignore_last_newline(result.output)
    exp = ignore_last_newline(result.expected_output)
    if out == exp:
        result.status = JudgeStatus.AC
        return result

    if equals_ignore_presentation_error(out, exp):
        result.status = JudgeStatus.PE
        return result

    result.status = JudgeStatus.WA
    return result
