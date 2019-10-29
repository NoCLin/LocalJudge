import os

import pytest

from lj.judger import do_compile, do_judge_run, JudgeStatus

import unittest
from pathlib import Path

CODE_DIR = (Path(__file__).parent / "code").resolve()
POJ_1000_DIR = CODE_DIR / "poj-1000"
os.environ["LJ_TEST"] = "TRUE"


class JudgeStatusTest(unittest.TestCase):
    def tearDown(self):
        pass

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def assert_status_poj_1000(self, src, status, time_limit=None, memory_limit=None):
        compile_result = do_compile(src)
        self.assertEqual(0, compile_result.code, compile_result.stdout)
        stdin = '1 2'
        expected_out = '3'
        judge_result = do_judge_run(compile_result.runnable,
                                    stdin=stdin,
                                    expected_out=expected_out,
                                    time_limit=time_limit,
                                    memory_limit=memory_limit
                                    )
        self.assertEqual(status, judge_result.status)
        return judge_result

    def test_AC(self):
        self.assert_status_poj_1000(POJ_1000_DIR / "poj-1000.c", JudgeStatus.AC)

    def test_WA(self):
        self.assert_status_poj_1000(POJ_1000_DIR / "test@WA.cpp", JudgeStatus.WA)

    def test_RE(self):
        self.assert_status_poj_1000(POJ_1000_DIR / "test@RE.cpp", JudgeStatus.RE)

    def test_CE(self):
        compile_result = do_compile(POJ_1000_DIR / "test@CE.cpp")
        self.assertNotEqual(0, compile_result.code)

    def test_MLE(self):
        path_1m = POJ_1000_DIR / "test@memory-MLE-1M-limit-1M.cpp"
        path_max = POJ_1000_DIR / "test@memory-MLE-max-limit-1M.cpp"

        # NOTE: windows path_1M rss: 5341184
        self.assert_status_poj_1000(path_1m, JudgeStatus.AC, memory_limit=6 * 1024 * 1024, )
        self.assert_status_poj_1000(path_1m, JudgeStatus.MLE, memory_limit=1024 * 1024, )
        self.assert_status_poj_1000(path_max, JudgeStatus.MLE, memory_limit=2 * 1024 * 1024, )

    def test_OLE(self):
        pass

    def test_TLE(self):
        path_1s = POJ_1000_DIR / "test@time-TLE-1s-limit-1s.cpp"
        path_endless = POJ_1000_DIR / "test@time-TLE-endless-limit-1s.cpp"

        self.assert_status_poj_1000(path_1s, JudgeStatus.TLE, time_limit=999.9, )
        self.assert_status_poj_1000(path_1s, JudgeStatus.AC, time_limit=1500.1, )
        self.assert_status_poj_1000(path_endless, JudgeStatus.TLE, time_limit=100, )


if __name__ == '__main__':
    pytest.main()
