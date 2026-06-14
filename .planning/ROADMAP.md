# Roadmap — gemini-nano

**Milestone:** v1.0 Research Baseline
**Granularity:** Standard
**Coverage:** 5/5 requirements mapped

## Phases

- [ ] **Phase 1: CI Setup** - GitHub Actions workflow lints and validates the project on every push
- [ ] **Phase 2: Component Completion** - chrome-bridge gets a real health test; python-mediapipe gets graceful fallback and CLI argument
- [ ] **Phase 3: Unified README** - Single README documents the architecture and quick-start for all components

## Phase Details

### Phase 1: CI Setup
**Goal**: Every push to the repo triggers automated validation that catches regressions in api-server and confirms chrome-bridge installs cleanly
**Depends on**: Nothing (first phase)
**Requirements**: CI-01
**Success Criteria** (what must be TRUE):
  1. A push to any branch triggers the GitHub Actions workflow without manual intervention
  2. `api-server/` Python dependencies install and ruff lint passes with no errors
  3. `chrome-bridge/` npm dependencies install cleanly via `npm ci`
  4. The workflow completes green on a machine without Ollama (test_api.py skipped or collected-only)
**Plans**: TBD

### Phase 2: Component Completion
**Goal**: Users can run python-mediapipe/run_nano.py without a cryptic crash when the model is absent, and chrome-bridge has an automated health check that runs without Chrome
**Depends on**: Phase 1
**Requirements**: NANO-01, NANO-02, TEST-01
**Success Criteria** (what must be TRUE):
  1. Running `python run_nano.py` with no `model.task` file prints a clear download instruction and exits with code 0
  2. Running `python run_nano.py --model-path /custom/path.task` uses the specified path (with same graceful fallback if absent)
  3. Running `npm test` in `chrome-bridge/` starts a server, hits `/health`, asserts `{"status": "ok"}`, and exits 0 — no Chrome installation required
  4. The npm test is included in the CI workflow (Phase 1 updated or CI-01 fully satisfied)
**Plans**: TBD

### Phase 3: Unified README
**Goal**: Any developer can understand the project architecture and start each component in under 5 minutes using only the README
**Depends on**: Phase 2
**Requirements**: DOC-01
**Success Criteria** (what must be TRUE):
  1. `gemini-nano/README.md` exists and contains a component table with directory, language, port, and status columns
  2. README contains a Mermaid architecture diagram showing how api-server, chrome-bridge, chrome-demo, and python-mediapipe relate
  3. README contains quick-start commands (copy-pasteable) for each component
  4. README links to SETUP.md for Chrome flag configuration details
**Plans**: TBD
**UI hint**: yes

## Progress Table

| Phase | Plans Complete | Status | Completed |
|---|---|---|---|
| 1. CI Setup | 0/1 | Not started | - |
| 2. Component Completion | 0/3 | Not started | - |
| 3. Unified README | 0/1 | Not started | - |
