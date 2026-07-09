# Setup

## Quick start

### API server

```bash
cd api-server
python -m venv .venv
pip install -r requirements.txt
python app.py
```

### Chrome bridge

```bash
cd chrome-bridge
npm install
npm start
```

### Python MediaPipe

```bash
cd python-mediapipe
pip install -r requirements.txt
python run_nano.py "What is Gemini Nano?"
```

### Chrome demo

Open `chrome-demo/index.html` in Chrome Canary and enable:

- `chrome://flags/#prompt-api-for-gemini-nano`
- `chrome://flags/#optimization-guide-on-device-model`

## Notes

- `chrome-bridge` depends on Chrome Canary support for the Prompt API.
- `python-mediapipe` prints download instructions when the model asset is absent.
- The repo intentionally keeps these paths separate rather than forcing a shared build.
