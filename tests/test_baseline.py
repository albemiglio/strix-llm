import unittest

from strix_llm.checks import Status, check_vram_split
from strix_llm.baseline import BASELINE

MIB = 1024  # 1 GiB expressed in MiB


class CheckVramSplit(unittest.TestCase):
    def test_large_split_ok(self):
        self.assertEqual(check_vram_split(96 * MIB, 64 * MIB).status, Status.OK)

    def test_small_split_warns_with_fix(self):
        c = check_vram_split(8 * MIB, 64 * MIB)
        self.assertEqual(c.status, Status.WARN)
        self.assertTrue(c.fix)

    def test_unknown_split_warns_with_fix(self):
        c = check_vram_split(None, 64 * MIB)
        self.assertEqual(c.status, Status.WARN)
        self.assertTrue(c.fix)


class BaselineSanity(unittest.TestCase):
    def test_recommended_vram_fits_in_unified_pool(self):
        self.assertGreater(BASELINE.min_gpu_vram_mib, 0)
        self.assertLessEqual(
            BASELINE.min_gpu_vram_mib, BASELINE.min_unified_gib * 1024
        )


if __name__ == "__main__":
    unittest.main()
