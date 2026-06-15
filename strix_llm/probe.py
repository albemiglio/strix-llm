"""System probes for the doctor command (the impure half).

Every probe degrades gracefully: if it cannot read what it needs, it returns
None and the matching check reports that instead of crashing. That is why the
tool still runs something sensible on a laptop that is not a Framework Desktop.
"""
from __future__ import annotations

import os
import platform
import shutil


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


def detect_llama() -> tuple[str | None, bool | None]:
    path = (
        shutil.which("llama-cli")
        or shutil.which("llama-server")
        or shutil.which("main")
    )
    # Cheaply verifying a ROCm/HIP build is not reliable yet, so report unknown.
    return path, None
