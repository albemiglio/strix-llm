"""strix-llm command line interface."""
from __future__ import annotations

import argparse
import platform
import shutil
import sys


def _check(name: str, ok: bool, detail: str = "") -> None:
    mark = "ok" if ok else "--"
    line = f"  [{mark}] {name}"
    if detail:
        line += f": {detail}"
    print(line)


def cmd_doctor(args: argparse.Namespace) -> int:
    """Detect the hardware and sanity-check the local setup.

    Early skeleton. On a Framework Desktop this grows into a full validation of
    the VRAM/GTT split, ROCm version, kernel parameters and the llama.cpp build
    against a known-good baseline.
    """
    print("strix-llm doctor (work in progress)\n")
    print(f"  system : {platform.system()} {platform.release()} ({platform.machine()})")

    rocminfo = shutil.which("rocminfo")
    _check("rocminfo", rocminfo is not None, rocminfo or "not found in PATH")

    llama = shutil.which("llama-cli") or shutil.which("main")
    _check("llama.cpp", llama is not None, llama or "not found in PATH")

    if platform.system() != "Linux":
        print("\n  note: full detection targets Linux on Ryzen AI Max+ 395 (Strix Halo).")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    print(f"run: preset '{args.preset}' is not wired up yet (work in progress).")
    return 1


def cmd_bench(args: argparse.Namespace) -> int:
    print("bench: harness not implemented yet (work in progress).")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strix-llm",
        description="Known-good local LLM inference on the Framework Desktop (Strix Halo).",
    )
    sub = parser.add_subparsers(dest="command")

    d = sub.add_parser("doctor", help="detect hardware and check the local setup")
    d.set_defaults(func=cmd_doctor)

    r = sub.add_parser("run", help="launch a model preset")
    r.add_argument("preset", help="name of the model preset to run")
    r.set_defaults(func=cmd_run)

    b = sub.add_parser("bench", help="run the benchmark harness")
    b.set_defaults(func=cmd_bench)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
