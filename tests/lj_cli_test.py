import unittest
from subprocess import CalledProcessError, check_output, PIPE, STDOUT, Popen
from pathlib import Path
import json

from lj.judger import JudgeStatus

CODE_DIR = (Path(__file__).parent / "code").resolve()
POJ_1000_DIR = CODE_DIR / "poj-1000"
POJ_1000_DIR_STR = str(POJ_1000_DIR)


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


class CommandLineTest(unittest.TestCase):

    def check_poj_1000(self, code, data):
        self.assertEqual(0, code, data)
        lines = data.splitlines()

        self.assertNotEqual(-1, lines[3].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[4].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[5].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[6].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[7].find(JudgeStatus.AC), data)
        self.assertNotEqual(-1, lines[8].find(JudgeStatus.WA), data)

    def check_poj_1000_json(self, code, data):
        self.assertEqual(0, code, data)
        obj = json.loads(data)

        self.assertEqual(0, obj["compile"]["code"], obj)

        self.assertEqual(JudgeStatus.AC, obj["cases"][0]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][1]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][2]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][3]["status"], obj)
        self.assertEqual(JudgeStatus.AC, obj["cases"][4]["status"], obj)
        self.assertEqual(JudgeStatus.WA, obj["cases"][5]["status"], obj)

    def test_lj_c(self):
        code, data = getstatusoutput(["lj", "poj-1000.c"], cwd=POJ_1000_DIR_STR)
        self.check_poj_1000(code, data)

    def test_lj_cpp(self):
        code, data = getstatusoutput(["lj", "poj-1000.cpp"], cwd=POJ_1000_DIR_STR)
        self.check_poj_1000(code, data)

    def test_lj_no_ext(self):
        code, data = getstatusoutput(["lj", "poj-1000"], cwd=POJ_1000_DIR_STR)
        self.check_poj_1000(code, data)

    def test_lj_py(self):
        code, data = getstatusoutput(["lj", "poj-1000.py"], cwd=POJ_1000_DIR_STR)
        self.check_poj_1000(code, data)

    def test_lj_json(self):
        code, data = getstatusoutput(["lj", "poj-1000.c", "--json"], cwd=POJ_1000_DIR_STR)
        self.check_poj_1000_json(code, data)

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

    def check_lj_json_status_poj_1000(self, src, status):
        in_file = POJ_1000_DIR / "poj-1000" / "1.in"
        eout_file = POJ_1000_DIR / "poj-1000" / "1.out"
        commands = ["lj", str(src), "--json",
                    "-i", str(in_file),
                    "-eo", str(eout_file)]
        print(" ".join(commands))
        code, data = getstatusoutput(commands, cwd=POJ_1000_DIR_STR)
        print("done")
        self.assertEqual(0, code, data)
        obj = json.loads(data)
        self.assertEqual(0, obj["compile"]["code"], obj)
        self.assertEqual(status, obj["cases"][0]["status"], obj)

    def test_TLE_limit_in_src(self):
        # 详细测试在 judge_status_test.py 中

        self.check_lj_json_status_poj_1000("time-AC-1s-limit-2s.cpp", JudgeStatus.AC)
        self.check_lj_json_status_poj_1000("time-TLE-1s-limit-1s.cpp", JudgeStatus.TLE)
        self.check_lj_json_status_poj_1000("time-TLE-endless-limit-1s.cpp", JudgeStatus.TLE)

    def test_MLE_limit_in_src(self):
        self.check_lj_json_status_poj_1000("memory-AC-1M-limit-2M.cpp", JudgeStatus.AC)
        self.check_lj_json_status_poj_1000("memory-MLE-1M-limit-1M.cpp", JudgeStatus.MLE)
        self.check_lj_json_status_poj_1000("memory-MLE-max-limit-1M.cpp", JudgeStatus.MLE)
