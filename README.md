# strix-llm

![ci](https://github.com/AlbeMiglio/strix-llm/actions/workflows/ci.yml/badge.svg)

Known-good local LLM inference on the Framework Desktop (Ryzen AI Max+ 395 / Strix Halo).

Running a 70B model on Strix Halo is very doable: up to 96 GB of the 128 GB unified pool can be handed to the Radeon 8060S iGPU, which is enough for Llama-70B at usable speeds. Getting there is the hard part. Today it means hand-tuning BIOS VRAM/GTT splits, kernel parameters, ROCm versions and llama.cpp build flags, following forum threads that go stale fast.

strix-llm is the layer that makes that path reproducible and maintained, so you can go from a fresh Framework Desktop to a running model in one command.

## What it does

- **`strix-llm doctor`** — detects the hardware and checks the configuration (VRAM/GTT split, ROCm, kernel, llama.cpp build) against a known-good baseline, then tells you exactly what to fix.
- **Model presets** — curated model + quantization presets sized to the unified-memory budget, each launchable with a single command and sane defaults.
- **Benchmarks** — a small harness that measures tokens/s, max context and power draw in a reproducible way, with published results per configuration.

It is not another inference engine. It sits on top of ROCm and llama.cpp and does the boring, fiddly integration work nobody wants to redo by hand.

## Install

```
pipx install git+https://github.com/AlbeMiglio/strix-llm
# or: pip install git+https://github.com/AlbeMiglio/strix-llm
```

## Usage

```
strix-llm doctor                          # check the machine and the local setup
strix-llm list                            # show curated model presets
strix-llm run llama-3.3-70b               # print the exact llama.cpp command to launch
strix-llm run llama-3.3-70b --model ~/models/llama-3.3-70b-q4.gguf
strix-llm bench --parse-file run.log      # tokens/sec from a saved llama.cpp log
```

Without `--model`, `run` prints the command it would launch and where to get the
model, so you see exactly what will happen before downloading tens of GB.

Example `doctor` output on a configured Framework Desktop:

```
strix-llm doctor

  [ok] os: Linux
  [ok] cpu: AMD Ryzen AI Max+ 395 w/ Radeon 8060S
  [ok] memory: 119 GiB unified
  [ok] vram-split: 96 GiB allocated to the iGPU
  [ok] rocm: ROCm 6.2.0
  [ok] llama.cpp: /usr/bin/llama-server (ROCm build)
```

`strix-llm doctor --json` prints the same checks in machine-readable form.

## Status

Early work in progress. `doctor`, the model presets (`list` / `run`) and llama.cpp
timing parsing work today; the live model run and published benchmarks land once it
runs on a Framework Desktop. Built test-first, with no external dependencies.

## Target hardware

- Framework Desktop / Ryzen AI Max+ 395 (Strix Halo), 128 GB unified memory
- Radeon 8060S iGPU, ROCm on Linux

## Roadmap

- [x] `doctor`: hardware, ROCm and config detection with remediation
- [x] Model + quant presets and one-command launch (`list` / `run`)
- [x] Benchmark parsing of llama.cpp timings
- [ ] Known-good baseline configs (BIOS notes, kernel params, ROCm pinning)
- [ ] Published benchmark results measured on real hardware
- [ ] Quantization / KV-cache tuning for unified memory

## Maintainer

Maintained by Alberto Migliorato ([@AlbeMiglio](https://github.com/AlbeMiglio)).

## License

MIT
