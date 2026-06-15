import unittest

from strix_llm.probe import linked_libs_have_rocm


class LinkedLibsHaveRocm(unittest.TestCase):
    def test_detects_hipblas(self):
        out = (
            "\tlibhipblas.so => /opt/rocm/lib/libhipblas.so (0x00007f...)\n"
            "\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6"
        )
        self.assertTrue(linked_libs_have_rocm(out))

    def test_detects_rocblas(self):
        self.assertTrue(
            linked_libs_have_rocm("librocblas.so.4 => /opt/rocm/lib/librocblas.so.4")
        )

    def test_cpu_only_build_is_false(self):
        out = (
            "\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6\n"
            "\tlibm.so.6 => /lib/x86_64-linux-gnu/libm.so.6"
        )
        self.assertFalse(linked_libs_have_rocm(out))


if __name__ == "__main__":
    unittest.main()
