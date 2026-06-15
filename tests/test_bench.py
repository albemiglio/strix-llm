import unittest

from strix_llm.bench import parse_timings

SAMPLE = """
llama_print_timings:        load time =    1234.00 ms
llama_print_timings: prompt eval time =     200.00 ms /    50 tokens (    4.00 ms per token,   250.00 tokens per second)
llama_print_timings:        eval time =    2000.00 ms /    64 runs   (   31.25 ms per token,    32.00 tokens per second)
llama_print_timings:       total time =    3500.00 ms
"""


class ParseTimings(unittest.TestCase):
    def test_extracts_prompt_and_generation_tps(self):
        r = parse_timings(SAMPLE)
        self.assertAlmostEqual(r.prompt_tps, 250.0)
        self.assertAlmostEqual(r.gen_tps, 32.0)

    def test_empty_output_is_none(self):
        r = parse_timings("")
        self.assertIsNone(r.prompt_tps)
        self.assertIsNone(r.gen_tps)


if __name__ == "__main__":
    unittest.main()
