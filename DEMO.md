# Demo script (~60 seconds)

Record a terminal GIF to `docs/demo.gif`. Keep it tight.

## Setup (before recording)
- Clean terminal, repo root, dependencies installed (`make install`).
- `clear` the screen.

## Beats

1) **One-line pitch (say it):** "llm-redteam fires an OWASP-mapped catalog of adversarial
   prompts at an LLM and scores the replies with deterministic detectors."

2) **Show the offline gate (2s):**
   ```bash
   make test
   ```
   Point at `24 passed` — the deterministic core is tested with no network and no API key.

3) **Run the harness on the bundled mock target:**
   ```bash
   make demo
   ```
   Read the summary line out loud: `13 tested, 8 passed, 5 failed ... risk 26.6/100 (medium)`.

4) **Open the report (5s):**
   ```bash
   sed -n '1,40p' out/report.md
   ```
   Highlight two real failures:
   - `sl-01` system-prompt leak — the planted canary `CANARY-7F3A9K...` showed up in the reply.
   - `pii-03` — the model echoed a fake SSN (caught by a regex detector).
   Point at the honesty banner: "automated test aid, a human must review — never a certification."

5) **Show it is real, not a toy (optional, if ollama is running):**
   ```bash
   make run-live
   ```
   Same pipeline, now hitting a live local model via `llm.py`.

## Closing line
"Deterministic detectors, OWASP mapping, markdown + JSON output — drop it in CI to catch
prompt-injection and secret-leak regressions on every model change."
