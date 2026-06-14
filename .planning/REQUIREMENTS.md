# Requirements — gemini-nano

**Milestone:** v1.0 Research Baseline

## v1 Requirements

### CI

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| CI-01 | GitHub Actions CI runs on push/PR: lint `api-server/` with ruff, run `api-server/test_api.py` as a connectivity-skippable check, and confirm `chrome-bridge` installs cleanly (`npm ci`) | Must | `test_api.py` requires a live Ollama server — CI should run it with `--co` (collect-only) or skip via env flag; npm test does not exist yet |

### MediaPipe

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| NANO-01 | `python-mediapipe/run_nano.py` adds graceful fallback: if `model.task` file is absent, print a clear download instruction and exit with code 0 (not a traceback) | Must | Current code crashes with FileNotFoundError when model is missing |
| NANO-02 | `run_nano.py` accepts `--model-path` CLI argument so callers can specify a non-default `.task` file path | Should | Improves usability without changing default behavior |

### Testing

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| TEST-01 | `chrome-bridge/` has a `test` script in `package.json` that starts the server, hits `/health`, asserts `status === "ok"`, and exits — no Chrome/Puppeteer required for the health check | Must | Server already has `/health`; test should bypass `launchBrowser()` or use a lightweight separate script |

### Documentation

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| DOC-01 | `gemini-nano/README.md` exists with: component table, architecture Mermaid diagram showing data flow between components, and quick-start commands for each component | Must | Currently only `CLAUDE.md` and `SETUP.md` exist; no user-facing README |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| CI-01 | Phase 1 | Pending |
| TEST-01 | Phase 2 | Pending |
| NANO-01 | Phase 2 | Pending |
| NANO-02 | Phase 2 | Pending |
| DOC-01 | Phase 3 | Pending |
