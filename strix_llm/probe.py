"""System probes for the doctor command (the impure half).

Every probe degrades gracefully: if it cannot read what it needs, it returns
None and the matching check reports that instead of crashing. That is why the
tool still runs something sensible on a laptop that is not a Framework Desktop.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess


def detect_system() -> str:
    return platform.system()


def detect_cpu_model() -> str | None:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or None


def detect_total_memory() -> int | None:
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError, AttributeError):
        return None


def detect_rocm_version() -> str | None:
    try:
        with open("/opt/rocm/.info/version", encoding="utf-8") as fh:
            return fh.readline().strip() or None
    except OSError:
        return None


def linked_libs_have_rocm(ldd_output: str) -> bool:
    text = ldd_output.lower()
    return any(
        lib in text for lib in ("libhipblas", "librocblas", "libamdhip", "librocm")
    )


def detect_llama() -> tuple[str | None, bool | None]:
    path = (
        shutil.which("llama-cli")
        or shutil.which("llama-server")
        or shutil.which("main")
    )
    if path is None:
        return None, None
    try:
        out = subprocess.run(
            ["ldd", path], capture_output=True, text=True, timeout=5
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return path, None
    if not out:
        return path, None
    return path, linked_libs_have_rocm(out)


def detect_gpu_vram_mib() -> int | None:
    for path in (
        "/sys/class/drm/card0/device/mem_info_vram_total",
        "/sys/class/drm/card1/device/mem_info_vram_total",
    ):
        try:
            with open(path, encoding="utf-8") as fh:
                return int(fh.read().strip()) // (1024 * 1024)
        except (OSError, ValueError):
            continue
    return None
