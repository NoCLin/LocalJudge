import json
import os
import unittest
from pathlib import Path
from subprocess import CalledProcessError, check_output, PIPE, STDOUT, Popen

import pytest

from lj.common import TEMP_DIR_NAME
from lj.judger import JudgeStatus

CODE_DIR = (Path(__file__).parent / "code").resolve()
POJ_1000_DIR = CODE_DIR / "poj-1000"
POJ_1000_DIR_STR = str(POJ_1000_DIR)
os.environ["LJ_TEST"] = "TRUE"


def getstatusoutput(cmd, cwd):
    try:
        data = check_output(cmd, cwd=cwd, universal_newlines=True, stderr=STDOUT)
        exitcode = 0
    except CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


def capture_lj_command_output(commands):
    p = Popen(commands, universal_newlines=True,
              stdin=PIPE, stdout=PIPE, cwd=str(POJ_1000_DIR))
    stdout, _ = p.communicate()
    return stdout


class CommandLineTest(unittest.TestCase):

    def check_poj_1000(self, data):
        lines = data.splitlines()

        self.assertNotEqual(-1, lines[3].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[4].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[5].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[6].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[7].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[8].find(JudgeStatus.WA), data)

    def check_poj_1000_json(self, data):
        obj = json.loads(data)

        self.assertEqual(0, obj["compile"]["code"], obj)

        self.assertEqual(JudgeStatus.AC, obj["cases"][0]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][1]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][2]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][3]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][4]["status"], obj)
        self.assertEqual(JudgeStatus.WA, obj["cases"][5]["status"], obj)

    @classmethod
    def tearDownClass(cls):
        tmp = POJ_1000_DIR / TEMP_DIR_NAME
        if tmp.is_dir():
            directory = str(tmp)
            print("removing " + directory)
            import shutil
            shutil.rmtree(directory, onerror=print)

    def test_lj_c(self):
        data = capture_lj_command_output(["lj", str(POJ_1000_DIR / "poj-1000.c")])
        self.check_poj_1000(data)

    def test_lj_cpp(self):
        data = capture_lj_command_output(["lj", str(POJ_1000_DIR / "poj-1000.cpp")])
        self.check_poj_1000(data)

    def test_lj_no_ext(self):
        data = capture_lj_command_output(["lj", str(POJ_1000_DIR / "poj-1000")])
        self.check_poj_1000(data)

    def test_lj_py(self):
        data = capture_lj_command_output(["lj", str(POJ_1000_DIR / "poj-1000.py")])
        self.check_poj_1000(data)

    def test_lj_json(self):
        data = capture_lj_command_output(["lj", str(POJ_1000_DIR / "poj-1000.cpp"), "--json", ])
        self.check_poj_1000_json(data)

    def test_lj_run(self):
        command_list = [
            ["lj", "run", "poj-1000.c"],
            ["ljr", "poj-1000.c"]
        ]

        for command in command_list:
            p = Popen(command, universal_newlines=True,
                      stdin=PIPE, stdout=PIPE, cwd=str(POJ_1000_DIR))
            stdout, _ = p.communicate("1 2")
            self.assertNotEqual(-1, stdout.find("Process Exit Code: 0"), stdout)
            self.assertNotEqual(-1, stdout.find("3\n"), stdout)

    def check_lj_json_first_status(self, data, status):
        obj = json.loads(data)
        self.assertEqual(0, obj["compile"]["code"], obj)
        self.assertEqual(status, obj["cases"][0]["status"], obj)

    def test_TLE_limit_in_src(self):
        # 详细测试在 judge_status_test.py 中
        commands = ["lj", str(POJ_1000_DIR / "test@time-AC-1s-limit-2s.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.AC)

        commands = ["lj", str(POJ_1000_DIR / "test@time-TLE-1s-limit-1s.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.TLE)

        commands = ["lj", str(POJ_1000_DIR / "test@time-TLE-endless-limit-1s.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.TLE)

    def test_MLE_limit_in_src(self):
        commands = ["lj", str(POJ_1000_DIR / "test@memory-AC-1M-limit-6M.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.AC)

        commands = ["lj", str(POJ_1000_DIR / "test@memory-MLE-1M-limit-1M.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.MLE)

        commands = ["lj", str(POJ_1000_DIR / "test@memory-MLE-max-limit-1M.cpp"), "--json", ]
        self.check_lj_json_first_status(capture_lj_command_output(commands), JudgeStatus.MLE)


if __name__ == '__main__':
    pytest.main()
