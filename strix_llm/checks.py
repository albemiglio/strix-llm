"""Diagnostic checks for the strix-llm doctor command.

These functions are pure: they take already-probed values and return a Check
describing the result. Gathering those values from the system lives in
strix_llm.probe, so this logic can be tested without any AMD hardware.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

GIB = 1024 ** 3

# A "128 GB" machine reports a little less after firmware reservation, so allow
# some margin before flagging the memory as undersized.
MIN_UNIFIED_GIB = 110


class Status(Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass(frozen=True)
class Check:
    name: str
    status: Status
    detail: str = ""
    fix: str = ""


def check_os(system: str) -> Check:
    if system == "Linux":
        return Check("os", Status.OK, "Linux")
    return Check(
        "os",
        Status.SKIP,
        f"{system}: full hardware detection only runs on Linux",
        fix="Run strix-llm on the Framework Desktop (Linux) for real results.",
    )


def check_cpu(model: str | None) -> Check:
    if not model:
        return Check("cpu", Status.WARN, "could not detect the CPU model")
    if "ryzen ai max" in model.lower():
        return Check("cpu", Status.OK, model)
    return Check(
        "cpu",
        Status.WARN,
        f"{model}: not a Ryzen AI Max (Strix Halo); tuning assumes that APU",
    )


def check_memory(total_bytes: int | None) -> Check:
    if total_bytes is None:
        return Check("memory", Status.WARN, "could not detect total memory")
    gib = total_bytes / GIB
    if gib >= MIN_UNIFIED_GIB:
        return Check("memory", Status.OK, f"{gib:.0f} GiB unified")
    return Check(
        "memory",
        Status.WARN,
        f"{gib:.0f} GiB: below the 128 GB target, large presets may not fit",
    )


def check_rocm(version: str | None) -> Check:
    if version:
        return Check("rocm", Status.OK, f"ROCm {version}")
    return Check(
        "rocm",
        Status.FAIL,
        "ROCm not found",
        fix="Install ROCm and make sure rocminfo is on PATH.",
    )


def check_llama(path: str | None, has_rocm_build: bool | None) -> Check:
    if not path:
        return Check(
            "llama.cpp",
            Status.FAIL,
            "llama.cpp not found",
            fix="Build llama.cpp with ROCm/HIP support and put it on PATH.",
        )
    if has_rocm_build is True:
        return Check("llama.cpp", Status.OK, f"{path} (ROCm build)")
    if has_rocm_build is False:
        return Check(
            "llama.cpp",
            Status.WARN,
            f"{path}: CPU-only build, no GPU offload",
            fix="Rebuild llama.cpp with ROCm/HIP support.",
        )
    return Check(
        "llama.cpp",
        Status.WARN,
        f"{path}: found, but could not verify ROCm support",
    )


def overall_exit_code(checks: list[Check]) -> int:
    return 1 if any(c.status is Status.FAIL for c in checks) else 0
