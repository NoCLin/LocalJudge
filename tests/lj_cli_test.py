import unittest
from subprocess import CalledProcessError, check_output, PIPE, STDOUT, Popen
from pathlib import Path
import json

from lj.judger import JudgeStatus

PROB_DIR = (Path(__file__).parent / "problems").resolve().absolute()


def getstatusoutput(cmd):
    try:
        data = check_output(cmd,
                            cwd=str(PROB_DIR),
                            universal_newlines=True,
                            stderr=STDOUT)
        exitcode = 0
    except CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


class LocalJudgeCLITest(unittest.TestCase):

    def check_poj_1000(self, code, data):
        self.assertEqual(0, code)
        lines = data.splitlines()
        self.assertNotEqual(-1, lines[3].find(JudgeStatus.AC))
        self.assertNotEqual(-1, lines[4].find(JudgeStatus.AC))
        self.assertNotEqual(-1, lines[5].find(JudgeStatus.AC))
        self.assertNotEqual(-1, lines[6].find(JudgeStatus.AC))
        self.assertNotEqual(-1, lines[7].find(JudgeStatus.AC))
        self.assertNotEqual(-1, lines[8].find(JudgeStatus.WA))

    def test_lj_c(self):
        code, data = getstatusoutput(["lj", "poj-1000.c"])
        self.check_poj_1000(code, data)

    def test_lj_no_ext(self):
        code, data = getstatusoutput(["lj", "poj-1000"])
        self.check_poj_1000(code, data)

    def test_lj_py(self):
        code, data = getstatusoutput(["lj", "poj-1000.py"])
        self.check_poj_1000(code, data)

    def test_lj_json(self):
        code, data = getstatusoutput(["lj", "poj-1000.c", "--json"])
        obj = json.loads(data)

        self.assertEqual(0, obj["compile"]["code"])
        self.assertEqual(JudgeStatus.AC, obj["cases"][0]["status"])
        self.assertEqual(JudgeStatus.AC, obj["cases"][1]["status"])
        self.assertEqual(JudgeStatus.AC, obj["cases"][2]["status"])
        self.assertEqual(JudgeStatus.AC, obj["cases"][3]["status"])
        self.assertEqual(JudgeStatus.AC, obj["cases"][4]["status"])
        self.assertEqual(JudgeStatus.WA, obj["cases"][5]["status"])

    def test_lj_run(self):
        p = Popen(["lj", "run", "poj-1000.c"],
                  stdin=PIPE, stdout=PIPE, cwd=PROB_DIR)
        stdout, _ = p.communicate("1 2".encode())
        print(stdout)
        self.assertNotEqual(-1, stdout.find(b"Process Exit Code: 0"))
        self.assertNotEqual(-1, stdout.find(b"3\n"))

        p = Popen(["ljr", "poj-1000.c"], stdin=PIPE, stdout=PIPE, cwd=PROB_DIR)
        stdout, _ = p.communicate("1 2".encode())
        self.assertNotEqual(-1, stdout.find(b"Process Exit Code: 0"))
        self.assertNotEqual(-1, stdout.find(b"3\n"))
