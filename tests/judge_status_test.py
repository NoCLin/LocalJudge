from lj.judger import do_compile, do_judge_run, JudgeStatus
from lj.utils import obj_json_dumps

import unittest
import shutil
from pathlib import Path

CASE_DIR = (Path(__file__).parent / "cases").resolve().absolute()


class LocalJudgeStatusTest(unittest.TestCase):  # 继承unittest.TestCase
    def tearDown(self):
        pass
        print("=" * 10)

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        directory = str(CASE_DIR / ".local_judge")
        print("removing " + directory)
        shutil.rmtree(directory, onerror=print)

    def assert_status(self, src, status, time_limit=None, memory_limit=None):
        compile_result = do_compile(src)
        self.assertEqual(0, compile_result.code)
        stdin = '1 2'
        expected_out = '3'
        judge_result = do_judge_run(compile_result.runnable,
                                    stdin=stdin,
                                    expected_out=expected_out,
                                    time_limit=None,
                                    memory_limit=None
                                    )
        print(compile_result.params["src"])
        print(obj_json_dumps(judge_result))
        self.assertEqual(status, judge_result.status)

    def test_AC(self):
        self.assert_status(CASE_DIR / "AC.cpp", JudgeStatus.AC)

    def test_WA(self):
        self.assert_status(CASE_DIR / "WA.cpp", JudgeStatus.WA)

    def test_CE(self):
        compile_result = do_compile(CASE_DIR / "CE.cpp")
        print(compile_result.params["src"])
        print(obj_json_dumps(compile_result))
        self.assertNotEqual(0, compile_result.code)

    def test_MLE(self):
        pass

    def test_OLE(self):
        pass

    def test_TLE(self):
        pass


if __name__ == '__main__':
    unittest.main()
