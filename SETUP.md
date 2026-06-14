# Local LLM API — Setup Guide

Machine: HP ZBook Firefly 16 G11 | Intel Core Ultra 7 155H | 32 GB RAM | NVIDIA RTX A500 4 GB

---

## Quick start (Ollama API on port 9000)

```powershell
cd C:\PersonalRepo\gemini-nano\api-server
.\start.ps1
```

Open http://localhost:9000 in any browser to use the web UI.

### Calling from your other projects

```python
import httpx

resp = httpx.post("http://localhost:9000/v1/chat/completions", json={
    "model": "gemma3:12b",   # see model table below
    "messages": [{"role": "user", "content": "Hello!"}]
})
print(resp.json()["choices"][0]["message"]["content"])
```

OpenAI SDK compatible — just set `base_url="http://localhost:9000/v1"` and `api_key="local"`.

---

## Available models

| Model | Size | Speed | Best for |
|-------|------|-------|---------|
| `gemma3:12b` | 8.1 GB | Medium | **Best quality — use this by default** |
| `qwen3:8b` | 5.2 GB | Fast | Multilingual, thinking/reasoning mode |
| `phi3:mini` | 2.2 GB | Fast | Reasoning, structured output |
| `gemma3:1b` | 815 MB | Fastest | Latency-critical, embedded use |

Aliases work too: `"best"` → gemma3:12b, `"nano"` → gemma3:1b, `"qwen"` → qwen3:8b

---

## IMPORTANT — Fix before first use (non-ASCII username path bug)

The `ä` in your Windows username `KimHarjamäki` causes llama.cpp to fail loading
any model. Fix it once with these four commands (run PowerShell **as Administrator**):

```powershell
# 1. Junction: ASCII alias for the existing model folder (no data copied)
New-Item -ItemType Junction -Path "C:\ollama-models" -Target "C:\Users\KimHarjamäki\.ollama\models"

# 2. Persist the path for your user account
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "C:\ollama-models", "User")

# 3. Stop Ollama
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue

# 4. Restart Ollama tray app
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
```

---

## Chrome Built-in Gemini Nano (optional — requires Chrome Dev/Canary)

This lets you run actual Gemini Nano inside Chrome. Different from the Ollama models above.

1. Install Chrome Dev: https://www.google.com/chrome/dev/
2. Enable flags in Chrome:
   - `chrome://flags/#optimization-guide-on-device-model` → **Enabled BypassPerfRequirement**
   - `chrome://flags/#prompt-api-for-gemini-nano` → **Enabled**
3. Restart Chrome, go to `chrome://components/`, update **Optimization Guide On Device Model**
4. Open `chrome-demo/index.html` in Chrome — banner turns green when ready

Chrome bridge API (port 8081) — exposes window.ai as HTTP:
```powershell
cd C:\PersonalRepo\gemini-nano\chrome-bridge
.\start.ps1
# Then POST to http://localhost:8081/v1/chat/completions with model "gemini-nano"
```

---

## Folder structure

```
gemini-nano/
  SETUP.md                      <- you are here
  api-server/
    server.py                   <- FastAPI server (port 9000)
    start.ps1                   <- run this
    test_api.py                 <- smoke test all models
    requirements.txt
  chrome-bridge/
    server.js                   <- Chrome Gemini Nano HTTP bridge (port 8081)
    start.ps1
    package.json
  chrome-demo/
    index.html                  <- browser demo for Chrome built-in AI
  python-mediapipe/
    run_nano.py                 <- MediaPipe fallback (for when Google releases desktop weights)
    requirements.txt
```
