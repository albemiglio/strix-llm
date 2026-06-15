"""Parse llama.cpp timing output into tokens/sec figures.

llama.cpp prints a timings block at the end of a run. This pulls the prompt
(prefill) and generation rates out of it, so a captured log turns into numbers
the benchmark harness can publish.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_TPS = re.compile(r"([\d.]+)\s+tokens per second")


@dataclass(frozen=True)
class BenchResult:
    prompt_tps: float | None = None
    gen_tps: float | None = None


def parse_timings(output: str) -> BenchResult:
    prompt_tps = None
    gen_tps = None
    for line in output.splitlines():
        match = _TPS.search(line)
        if not match:
            continue
        value = float(match.group(1))
        low = line.lower()
        if "prompt eval time" in low:
            prompt_tps = value
        elif "eval time" in low:
            gen_tps = value
    return BenchResult(prompt_tps=prompt_tps, gen_tps=gen_tps)
