"""Curated model presets sized to the Framework Desktop unified-memory budget.

Each preset is a model + quantization known to run well within the iGPU VRAM
pool, plus the llama.cpp flags to launch it. approx_vram_gib is the rough
footprint at the listed context, so presets stay comfortably inside the budget.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    name: str
    description: str
    hf_repo: str
    hf_file: str
    ctx: int
    ngl: int = 99  # offload all layers to the iGPU
    approx_vram_gib: int = 0
    extra_flags: tuple[str, ...] = ()


PRESETS: dict[str, Preset] = {
    "llama-3.3-70b": Preset(
        name="llama-3.3-70b",
        description="Llama 3.3 70B Instruct, Q4_K_M - flagship general model",
        hf_repo="bartowski/Llama-3.3-70B-Instruct-GGUF",
        hf_file="Llama-3.3-70B-Instruct-Q4_K_M.gguf",
        ctx=8192,
        approx_vram_gib=43,
    ),
    "qwen2.5-72b": Preset(
        name="qwen2.5-72b",
        description="Qwen2.5 72B Instruct, Q4_K_M - strong multilingual and coding",
        hf_repo="bartowski/Qwen2.5-72B-Instruct-GGUF",
        hf_file="Qwen2.5-72B-Instruct-Q4_K_M.gguf",
        ctx=8192,
        approx_vram_gib=47,
    ),
    "llama-3.1-8b": Preset(
        name="llama-3.1-8b",
        description="Llama 3.1 8B Instruct, Q4_K_M - small and fast, good for smoke tests",
        hf_repo="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        hf_file="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        ctx=8192,
        approx_vram_gib=5,
    ),
}


def get_preset(name: str) -> Preset:
    try:
        return PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown preset '{name}'; run 'strix-llm list' to see options")


def build_command(
    preset: Preset,
    model_path: str,
    host: str = "127.0.0.1",
    port: int = 8080,
) -> list[str]:
    cmd = [
        "llama-server",
        "-m", model_path,
        "-ngl", str(preset.ngl),
        "-c", str(preset.ctx),
        "--host", host,
        "--port", str(port),
    ]
    cmd.extend(preset.extra_flags)
    return cmd
