import unittest

from strix_llm.checks import (
    Status,
    check_os,
    check_cpu,
    check_memory,
    check_rocm,
    check_llama,
    overall_exit_code,
)

GIB = 1024 ** 3


class CheckOS(unittest.TestCase):
    def test_linux_is_ok(self):
        self.assertEqual(check_os("Linux").status, Status.OK)

    def test_non_linux_is_skipped_with_guidance(self):
        c = check_os("Darwin")
        self.assertEqual(c.status, Status.SKIP)
        self.assertTrue(c.fix)


class CheckCPU(unittest.TestCase):
    def test_ryzen_ai_max_is_ok(self):
        c = check_cpu("AMD Ryzen AI Max+ 395 w/ Radeon 8060S")
        self.assertEqual(c.status, Status.OK)
        self.assertIn("Ryzen AI Max", c.detail)

    def test_other_cpu_warns(self):
        self.assertEqual(check_cpu("Apple M2").status, Status.WARN)

    def test_unknown_cpu_warns(self):
        self.assertEqual(check_cpu(None).status, Status.WARN)


class CheckMemory(unittest.TestCase):
    def test_full_unified_pool_ok(self):
        self.assertEqual(check_memory(128 * GIB).status, Status.OK)

    def test_small_memory_warns(self):
        self.assertEqual(check_memory(16 * GIB).status, Status.WARN)

    def test_unknown_memory_warns(self):
        self.assertEqual(check_memory(None).status, Status.WARN)


class CheckROCm(unittest.TestCase):
    def test_present_is_ok_and_reports_version(self):
        c = check_rocm("6.2.0")
        self.assertEqual(c.status, Status.OK)
        self.assertIn("6.2.0", c.detail)

    def test_absent_fails_with_fix(self):
        c = check_rocm(None)
        self.assertEqual(c.status, Status.FAIL)
        self.assertTrue(c.fix)


class CheckLlama(unittest.TestCase):
    def test_rocm_build_is_ok(self):
        c = check_llama("/usr/local/bin/llama-cli", True)
        self.assertEqual(c.status, Status.OK)

    def test_cpu_only_build_warns(self):
        c = check_llama("/usr/local/bin/llama-cli", False)
        self.assertEqual(c.status, Status.WARN)

    def test_missing_fails_with_fix(self):
        c = check_llama(None, None)
        self.assertEqual(c.status, Status.FAIL)
        self.assertTrue(c.fix)


class ExitCode(unittest.TestCase):
    def test_zero_when_no_failures(self):
        checks = [check_os("Linux"), check_cpu("AMD Ryzen AI Max+ 395")]
        self.assertEqual(overall_exit_code(checks), 0)

    def test_nonzero_when_any_fail(self):
        checks = [check_os("Linux"), check_rocm(None)]
        self.assertEqual(overall_exit_code(checks), 1)

    def test_warn_alone_does_not_fail(self):
        self.assertEqual(overall_exit_code([check_cpu("Apple M2")]), 0)


if __name__ == "__main__":
    unittest.main()
