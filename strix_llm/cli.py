"""strix-llm command line interface."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

from . import baseline, bench, checks, presets, probe
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
        checks.check_vram_split(
            probe.detect_gpu_vram_mib(), baseline.BASELINE.min_gpu_vram_mib
        ),
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
    if getattr(args, "json", False):
        print(json.dumps(checks.checks_to_dicts(check_list), indent=2))
    else:
        print(format_report(check_list))
    return checks.overall_exit_code(check_list)


def cmd_list(args: argparse.Namespace) -> int:
    for p in presets.PRESETS.values():
        print(f"  {p.name:14}  ~{p.approx_vram_gib:>2} GiB  {p.description}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    try:
        preset = presets.get_preset(args.preset)
    except KeyError as exc:
        print(f"error: {exc.args[0]}")
        return 1

    budget_gib = baseline.BASELINE.min_gpu_vram_mib / 1024
    if presets.exceeds_budget(preset, budget_gib):
        print(
            f"# warning: ~{preset.approx_vram_gib} GiB may exceed the "
            f"{budget_gib:.0f} GiB minimum split; raise the UMA/GTT split in BIOS"
        )

    model_path = args.model or f"<model>/{preset.hf_file}"
    cmd = presets.build_command(preset, model_path, host=args.host, port=args.port)

    if args.dry_run or not args.model:
        print(" ".join(cmd))
        if not args.model:
            print("\n# download:", " ".join(presets.download_command(preset)))
            print("# then re-run with --model <path> to launch")
        return 0

    if shutil.which(cmd[0]) is None:
        print(f"error: {cmd[0]} not found on PATH - run 'strix-llm doctor'")
        return 1
    return subprocess.call(cmd)


def cmd_bench(args: argparse.Namespace) -> int:
    if args.parse_file:
        try:
            with open(args.parse_file, encoding="utf-8") as fh:
                result = bench.parse_timings(fh.read())
        except OSError as exc:
            print(f"error: {exc}")
            return 1
        print(f"prompt eval : {result.prompt_tps} tok/s")
        print(f"generation  : {result.gen_tps} tok/s")
        return 0
    print("bench: a live run needs the target hardware.")
    print("meanwhile: strix-llm bench --parse-file <llama.cpp log>")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strix-llm",
        description="Known-good local LLM inference on the Framework Desktop (Strix Halo).",
    )
    sub = parser.add_subparsers(dest="command")

    d = sub.add_parser("doctor", help="detect hardware and check the local setup")
    d.add_argument("--json", action="store_true", help="machine-readable output")
    d.set_defaults(func=cmd_doctor)

    ls = sub.add_parser("list", help="list curated model presets")
    ls.set_defaults(func=cmd_list)

    r = sub.add_parser("run", help="build the launch command for a preset")
    r.add_argument("preset", help="preset name (see 'strix-llm list')")
    r.add_argument("--model", help="path to the GGUF model file")
    r.add_argument("--host", default="127.0.0.1")
    r.add_argument("--port", type=int, default=8080)
    r.add_argument(
        "--dry-run", action="store_true", help="print the command instead of launching"
    )
    r.set_defaults(func=cmd_run)

    b = sub.add_parser("bench", help="benchmark, or parse llama.cpp timings")
    b.add_argument("--parse-file", help="parse tokens/sec from a saved llama.cpp log")
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
