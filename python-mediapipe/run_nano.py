"""
Gemini Nano via MediaPipe LLM Inference API (desktop/PC).
NOTE: As of mid-2025, Google has not released Gemini Nano weights for
desktop Python — this script targets the MediaPipe LLM Inference task
which currently supports Gemma models locally. Swap in a Gemini Nano
.task file when Google makes one available for desktop.

Tested alternative: use Gemma 2B-IT (2 GB, runs fine on RTX A500 4GB).
"""

import argparse
import sys
from pathlib import Path


DEFAULT_MODEL_PATH = Path("model.task")

_DOWNLOAD_HINT = """\
No model file found at: {path}

Download a compatible model and place it at the path above, or pass --model-path:
  python run_nano.py --model-path /path/to/gemma2b-it.task "Your prompt here"

Gemma 2B-IT (recommended stand-in until Gemini Nano desktop weights ship):
  https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run on-device LLM inference via MediaPipe")
    parser.add_argument(
        "--model-path",
        default=None,
        help="Path to the .task model file (default: model.task in the current directory)",
    )
    parser.add_argument("prompt", nargs="*", help="Prompt text (default: built-in demo prompt)")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    model_path = Path(args.model_path) if args.model_path else DEFAULT_MODEL_PATH
    prompt_text = " ".join(args.prompt) if args.prompt else "What is a large language model?"

    if not model_path.exists():
        print(_DOWNLOAD_HINT.format(path=model_path), file=sys.stderr)
        return 0

    try:
        from mediapipe.tasks.python.text import llm_inference  # noqa: PLC0415

        options = llm_inference.LlmInferenceOptions(
            model_path=str(model_path),
            max_tokens=512,
            top_k=40,
            temperature=0.8,
        )
        with llm_inference.LlmInference.create_from_options(options) as llm:
            print(llm.generate_response(prompt_text))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Inference failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
