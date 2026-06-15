"""strix-llm command line interface."""
from __future__ import annotations

import argparse
import sys

from . import checks, probe
from .checks import Status

_MARKS = {
    Status.OK: "ok",
    Status.WARN: "!!",
    Status.FAIL: "XX",
    Status.SKIP: "--",
}


def _gather_checks() -> list[checks.Check]:
    path, rocm_build = probe.detect_llama()
    return [
        checks.check_os(probe.detect_system()),
        checks.check_cpu(probe.detect_cpu_model()),
        checks.check_memory(probe.detect_total_memory()),
        checks.check_rocm(probe.detect_rocm_version()),
        checks.check_llama(path, rocm_build),
    ]


def format_report(check_list: list[checks.Check]) -> str:
    lines = ["strix-llm doctor\n"]
    for c in check_list:
        line = f"  [{_MARKS[c.status]}] {c.name}"
        if c.detail:
            line += f": {c.detail}"
        lines.append(line)
        if c.fix and c.status is not Status.OK:
            lines.append(f"         -> {c.fix}")
    return "\n".join(lines)


def cmd_doctor(args: argparse.Namespace) -> int:
    check_list = _gather_checks()
    print(format_report(check_list))
    return checks.overall_exit_code(check_list)


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
