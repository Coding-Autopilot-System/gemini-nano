"""
Local LLM API server — unified OpenAI-compatible endpoint over Ollama.
Serves gemma3:12b, gemma3:1b, phi3:mini and qwen3:8b on port 9000.

Other projects call this exactly like the OpenAI API:
  POST http://localhost:9000/v1/chat/completions
  GET  http://localhost:9000/v1/models
"""

import asyncio
import json
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

OLLAMA_BASE = "http://localhost:11434"

MODELS = {
    "gemma3:12b": {
        "description": "Google Gemma 3 12B — best quality on this machine, GPU+RAM split",
        "alias": ["gemma12b", "best", "gemma"],
    },
    "qwen3:8b": {
        "description": "Qwen 3 8B — fast, multilingual, supports thinking mode",
        "alias": ["qwen3", "qwen"],
    },
    "gemma3:1b": {
        "description": "Google Gemma 3 1B — Gemini Nano equivalent, fastest",
        "alias": ["nano", "gemini-nano", "gemma3:1b"],
    },
    "phi3:mini": {
        "description": "Microsoft Phi-3 Mini — strong at reasoning, ~2.2 GB",
        "alias": ["phi3", "phi"],
    },
}

# Flatten aliases → canonical name
ALIAS_MAP: dict[str, str] = {}
for name, meta in MODELS.items():
    ALIAS_MAP[name] = name
    for alias in meta["alias"]:
        ALIAS_MAP[alias] = name


def resolve(model: str) -> str:
    canonical = ALIAS_MAP.get(model)
    if not canonical:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model}'. Available: {list(MODELS)}")
    return canonical


app = FastAPI(title="Local LLM API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── OpenAI-compatible endpoints ──────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "gemma3:1b"
    messages: list[Message]
    stream: bool = False
    temperature: float = 0.8
    max_tokens: int = 1024


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": name, "object": "model", "description": meta["description"], "aliases": meta["alias"]}
            for name, meta in MODELS.items()
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    model = resolve(req.model)

    ollama_payload = {
        "model": model,
        "messages": [m.model_dump() for m in req.messages],
        "stream": req.stream,
        "options": {"temperature": req.temperature, "num_predict": req.max_tokens},
    }

    if req.stream:
        return StreamingResponse(
            _stream_ollama(ollama_payload),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{OLLAMA_BASE}/api/chat", json=ollama_payload)
        resp.raise_for_status()
        data = resp.json()

    content = data["message"]["content"]
    return {
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": data.get("prompt_eval_count", 0), "completion_tokens": data.get("eval_count", 0)},
    }


async def _stream_ollama(payload: dict) -> AsyncIterator[bytes]:
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", f"{OLLAMA_BASE}/api/chat", json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("message", {}).get("content", "")
                done = chunk.get("done", False)
                sse = {
                    "id": "chatcmpl-local",
                    "object": "chat.completion.chunk",
                    "model": payload["model"],
                    "choices": [{"delta": {"content": delta}, "finish_reason": "stop" if done else None}],
                }
                yield f"data: {json.dumps(sse)}\n\n"
    yield "data: [DONE]\n\n"


# ── Simple browser UI ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def ui():
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><title>Local LLM API</title>
  <style>
    body{font-family:monospace;max-width:800px;margin:40px auto;padding:0 20px;background:#0d1117;color:#e6edf3}
    h1{color:#58a6ff}select,textarea{width:100%;box-sizing:border-box;background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:4px;padding:10px;font-family:monospace;font-size:.9em;margin-top:6px}
    button{background:#238636;color:#fff;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;margin-top:8px}
    button:disabled{background:#333;cursor:not-allowed}
    #out{margin-top:16px;white-space:pre-wrap;background:#161b22;border:1px solid #30363d;border-radius:4px;padding:12px;min-height:60px}
    label{color:#8b949e;font-size:.85em}
  </style>
</head>
<body>
  <h1>Local LLM API</h1>
  <label>Model</label><br>
  <select id="model">
    <option value="gemma3:12b">gemma3:12b — Best quality (recommended)</option>
    <option value="qwen3:8b">qwen3:8b — Fast, multilingual, thinking</option>
    <option value="gemma3:1b">gemma3:1b — Gemini Nano equivalent (fastest)</option>
    <option value="phi3:mini">phi3:mini — Microsoft Phi-3</option>
  </select>
  <br><br>
  <label>Prompt</label>
  <textarea id="prompt" rows="4">What is a large language model? Explain in 2 sentences.</textarea>
  <button id="go">Send</button>
  <div id="out">Response will appear here…</div>
  <script>
    document.getElementById('go').onclick = async () => {
      const btn = document.getElementById('go');
      const out = document.getElementById('out');
      btn.disabled = true; out.textContent = '';
      const resp = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          model: document.getElementById('model').value,
          messages: [{role:'user', content: document.getElementById('prompt').value}],
          stream: true
        })
      });
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        for (const line of dec.decode(value).split('\\n')) {
          if (!line.startsWith('data: ') || line.includes('[DONE]')) continue;
          try {
            const chunk = JSON.parse(line.slice(6));
            out.textContent += chunk.choices[0].delta.content || '';
          } catch {}
        }
      }
      btn.disabled = false;
    };
  </script>
</body>
</html>""")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=False)
