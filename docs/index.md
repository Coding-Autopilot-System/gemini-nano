# Gemini Nano

`gemini-nano` is the CAS research repo for local and browser-adjacent AI
experiments. It keeps four standalone components instead of one shared runtime,
so each surface can be validated independently.

## Components

| Component | Surface | Purpose |
|---|---|---|
| `api-server/` | Python HTTP API | FastAPI bridge for local model inference |
| `chrome-bridge/` | Node.js HTTP API | Exposes Chrome Prompt API over HTTP |
| `python-mediapipe/` | Python CLI | MediaPipe-based local inference path |
| `chrome-demo/` | Browser demo | Direct in-browser Gemini Nano prompt testing |

## What this repo is for

- Prototyping on-device and near-device model flows
- Verifying browser-native AI APIs without coupling them into the wider CAS stack
- Comparing local inference surfaces before promoting any one path into broader CAS architecture

## Validation surfaces

- `chrome-bridge/npm test`
- `python-mediapipe/run_nano.py`
- `api-server/test_api.py`

## Current positioning

This repo is intentionally experimental. It is useful as a proving ground and
integration reference, but it is not currently treated as a production CAS
service.
