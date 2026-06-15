# strix-llm

Known-good local LLM inference on the Framework Desktop (Ryzen AI Max+ 395 / Strix Halo).

Running a 70B model on Strix Halo is very doable: up to 96 GB of the 128 GB unified pool can be handed to the Radeon 8060S iGPU, which is enough for Llama-70B at usable speeds. Getting there is the hard part. Today it means hand-tuning BIOS VRAM/GTT splits, kernel parameters, ROCm versions and llama.cpp build flags, following forum threads that go stale fast.

strix-llm is the layer that makes that path reproducible and maintained, so you can go from a fresh Framework Desktop to a running model in one command.

## What it does

- **`strix-llm doctor`** — detects the hardware and checks the configuration (VRAM/GTT split, ROCm, kernel, llama.cpp build) against a known-good baseline, then tells you exactly what to fix.
- **Model presets** — curated model + quantization presets sized to the unified-memory budget, each launchable with a single command and sane defaults.
- **Benchmarks** — a small harness that measures tokens/s, max context and power draw in a reproducible way, with published results per configuration.

It is not another inference engine. It sits on top of ROCm and llama.cpp and does the boring, fiddly integration work nobody wants to redo by hand.

## Status

Early work in progress. The project is being built and validated on a Framework Desktop (Ryzen AI Max+ 395, 128 GB). The CLI skeleton and detection logic come first; presets and the benchmark harness follow.

## Target hardware

- Framework Desktop / Ryzen AI Max+ 395 (Strix Halo), 128 GB unified memory
- Radeon 8060S iGPU, ROCm on Linux

## Roadmap

- [ ] `doctor`: hardware and config detection and validation
- [ ] Known-good baseline configs (BIOS notes, kernel params, ROCm pinning)
- [ ] Model + quant presets with one-command launch
- [ ] Benchmark harness and published results
- [ ] Quantization / KV-cache tuning for unified memory

## Maintainer

Maintained by Alberto Migliorato ([@AlbeMiglio](https://github.com/AlbeMiglio)).

## License

MIT
