import unittest

from strix_llm.presets import PRESETS, Preset, get_preset, build_command


class Registry(unittest.TestCase):
    def test_known_preset_resolves(self):
        self.assertEqual(get_preset("llama-3.3-70b").name, "llama-3.3-70b")

    def test_unknown_preset_raises(self):
        with self.assertRaises(KeyError):
            get_preset("does-not-exist")

    def test_has_small_smoke_test_model(self):
        small = [p for p in PRESETS.values() if p.approx_vram_gib <= 8]
        self.assertTrue(small)


class BuildCommand(unittest.TestCase):
    def _preset(self):
        return Preset(
            name="t",
            description="d",
            hf_repo="r",
            hf_file="f.gguf",
            ctx=4096,
            ngl=99,
            approx_vram_gib=40,
        )

    def test_includes_model_path(self):
        cmd = build_command(self._preset(), "/models/f.gguf")
        self.assertIn("-m", cmd)
        self.assertEqual(cmd[cmd.index("-m") + 1], "/models/f.gguf")

    def test_offloads_to_gpu_and_sets_context(self):
        cmd = build_command(self._preset(), "/models/f.gguf")
        self.assertEqual(cmd[cmd.index("-ngl") + 1], "99")
        self.assertEqual(cmd[cmd.index("-c") + 1], "4096")

    def test_custom_port(self):
        cmd = build_command(self._preset(), "/m.gguf", port=1234)
        self.assertIn("1234", cmd)


class BudgetAndDownload(unittest.TestCase):
    def _preset(self, vram):
        return Preset(
            name="t",
            description="d",
            hf_repo="org/repo",
            hf_file="m.gguf",
            ctx=4096,
            ngl=99,
            approx_vram_gib=vram,
        )

    def test_within_budget(self):
        from strix_llm.presets import exceeds_budget

        self.assertFalse(exceeds_budget(self._preset(40), 64))

    def test_over_budget(self):
        from strix_llm.presets import exceeds_budget

        self.assertTrue(exceeds_budget(self._preset(80), 64))

    def test_download_command(self):
        from strix_llm.presets import download_command

        self.assertEqual(
            download_command(self._preset(40)),
            ["huggingface-cli", "download", "org/repo", "m.gguf"],
        )


if __name__ == "__main__":
    unittest.main()
