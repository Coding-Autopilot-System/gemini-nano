# gemini-nano

Experimental Gemini Nano integration demos. Explores on-device AI inference through four separate components — no shared build system; each component is standalone.

## Components

| Directory | Language | Purpose |
|---|---|---|
| `chrome-demo/` | HTML/JS | Browser demo page for Chrome's built-in Gemini Nano (Prompt API) |
| `python-mediapipe/` | Python | Gemini Nano via MediaPipe on-device inference |
| `api-server/` | Python | FastAPI server bridging Gemini Nano inference to HTTP |
| `chrome-bridge/` | Node.js/Express | Bridge server exposing Chrome's Prompt API over HTTP (`server.js`) |

## Local Development

**api-server** (Python):
```bash
cd gemini-nano/api-server
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# start server
python app.py  # or uvicorn if FastAPI
```

**chrome-bridge** (Node.js):
```bash
cd gemini-nano/chrome-bridge
npm install
.\start.ps1
```

**python-mediapipe**:
```bash
cd gemini-nano/python-mediapipe
pip install -r requirements.txt
python run_nano.py
```

**chrome-demo**: Open `chrome-demo/index.html` directly in Chrome Canary with `chrome://flags/#prompt-api-for-gemini-nano` enabled.

## Notes

- These are research/demo components, not production services
- `chrome-bridge` requires Chrome Canary with the Gemini Nano flag enabled
- `python-mediapipe` requires the MediaPipe Tasks GenAI package
- No shared config — each component is self-contained

## GSD Workflow

Use `/gsd:quick` for experimental work here. No formal phase planning required for this research area.
