# Project: gemini-nano

**Type:** Experimental / Research
**Core value:** Explore Gemini Nano on-device inference across three delivery surfaces: browser (Chrome Prompt API), Python (MediaPipe LLM Inference), and HTTP proxy (Ollama).

## Problem

On-device LLM inference is fragmented across APIs that are each in active development. This project maps the landscape by building thin working integrations for each surface so the CAS ecosystem can reference proven patterns when on-device inference matures.

## What Each Component Does

| Component | Language | Port | Status |
|---|---|---|---|
| `api-server/` | Python / FastAPI | 9000 | Working — proxies Ollama models (gemma3:12b, qwen3:8b, gemma3:1b, phi3:mini) via OpenAI-compatible HTTP API |
| `chrome-bridge/` | Node.js / Express + Puppeteer | 8081 | Working — launches Chrome headlessly, exposes `window.ai` Prompt API as HTTP; `/health` endpoint exists |
| `python-mediapipe/` | Python / MediaPipe Tasks | — | Stub — functional but targets Gemma weights, not yet Gemini Nano desktop weights (unavailable from Google as of mid-2025) |
| `chrome-demo/` | HTML/JS | — | Working — browser demo page for the Chrome Prompt API with status banner |

## Key Technical Facts

- `api-server/server.py` is a full FastAPI implementation with streaming support and alias resolution
- `api-server/test_api.py` is an **integration smoke test** — it calls a live Ollama server; there are no `pytest`-style `def test_*` functions
- `chrome-bridge/server.js` already has a `/health` endpoint returning `{status: "ok"}`
- `chrome-bridge/package.json` has no `test` script — only `start` and `install-deps`
- `python-mediapipe/run_nano.py` is nearly complete; it uses the correct MediaPipe LLM Inference API but lacks graceful fallback when the `.task` model file is absent
- Machine: HP ZBook Firefly 16 G11 — Intel Core Ultra 7 155H, 32 GB RAM, NVIDIA RTX A500 4 GB
- Non-ASCII username (`KimHarjamäki`) requires the `C:\ollama-models` junction workaround for llama.cpp

## Constraints

- No shared build system — each component is fully standalone
- Chrome bridge requires Chrome Dev or Canary with specific flags; unsuitable for headless CI inference testing
- MediaPipe desktop Gemini Nano weights are not yet publicly released; `run_nano.py` uses Gemma as a stand-in
- This is research/demo scope — not production services

## Milestone: v1.0 Research Baseline

Establish CI, complete the mediapipe stub, add a real health test for chrome-bridge, and write unified documentation.
