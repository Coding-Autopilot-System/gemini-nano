"""Manual integration smoke script for a live local LLM API server."""
import httpx

BASE = "http://localhost:9000"
PROMPT = "What is 2+2? Answer with just the number."

def ask(model: str) -> str:
    resp = httpx.post(
        f"{BASE}/v1/chat/completions",
        json={"model": model, "messages": [{"role": "user", "content": PROMPT}]},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    print("Testing local LLM API...\n")
    for model in ["gemma3:12b", "qwen3:8b", "gemma3:1b", "phi3:mini"]:
        print(f"[{model}] ", end="", flush=True)
        try:
            answer = ask(model)
            print(f"OK → {answer!r}")
        except Exception as e:
            print(f"FAIL → {e}")
