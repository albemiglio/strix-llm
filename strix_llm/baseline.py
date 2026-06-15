"""Known-good baseline for the Framework Desktop (Ryzen AI Max+ 395, 128 GB).

These are the targets strix-llm validates against and sizes presets for. They
are deliberately conservative and will be tightened with measurements once the
project runs on the real hardware.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Baseline:
    min_unified_gib: int = 110
    # Minimum the iGPU should be able to use as VRAM (UMA/GTT), in MiB.
    min_gpu_vram_mib: int = 64 * 1024
    rocm_min: str = "6.1"


BASELINE = Baseline()
