# CLAUDE.md — Valuation Engine
 
Context for Claude Code. Read this at the start of every session, then read
`docs/valuation-engine-build-guide.md` for the full build plan and current step.
 
## What this project is
 
A personal equity valuation engine in Python + Excel. One connected workflow with
four stages: **Screen → Score → Value → Size**. A Python script pulls company
financials via `yfinance` and writes CSVs; an Excel workbook reads those CSVs and,
driven by a single ticker cell, screens a universe, scores quality and safety,
runs a DCF and reverse DCF, and sizes a position. Goal: make smarter, math-backed
investment decisions, and serve as a portfolio/resume artifact.
 
The detailed, step-by-step build plan lives in `docs/valuation-engine-build-guide.md`.
That file is the source of truth for sequence and structure. Follow its phases and
checkpoints in order.
 
## Who I am
 
Undergrad, honors Economics with minors in Computer Science and Business. I can
write Python and read code. **I learn by building** — I want to understand the
*why* behind every step, not just copy working code.
 
## How to help me
 
- **Teach first, then do.** Before writing code or a command, explain the concept
  and why it matters in plain terms. Then give the code. Assume I want to understand it.
- **Work step by step.** Reference the build guide by phase/step number. Do one
  step, confirm it works against its checkpoint, then move on. Don't race ahead.
- **Check my logic.** If I paste a formula or a line of code, tell me whether it's
  right and why, not just yes/no.
- **Make me defend assumptions.** For any finance assumption (WACC, growth rate,
  terminal value, factor weights), make me state and justify the number. Don't pick
  it for me.
- **Be straight with me.** Don't over-praise. Tell me clearly when something is
  wrong or could be done better.
## Style
 
- No em dashes.
- Natural, direct tone. No filler.
- Concise. Lead with the answer.
## Environment & conventions
 
- macOS. Use `python3` and `pip3`, not `python`/`pip`.
- Stack: Python 3.11+, `yfinance`, `pandas`. Keep it minimal.
- Repo root is the project root. The folder named `Valuation-Model` here plays the
  role the build guide calls `valuation-engine/`.
- Data CSVs are written to `data/` and are git-ignored (`data/*.csv`). They are
  regenerable, so never commit them.
- Two data zones: `universe.csv` (one row per ticker, many tickers, few metrics —
  feeds Screener + Scorecard) and per-company statements files (one company, full
  multi-year statements — feeds the DCF).
- Never commit secrets. yfinance needs no API key, so there should be none here.
## Working with Git
 
- You may create files, run scripts, and stage/commit changes.
- Explain any terminal command before running it.
- Confirm with me before anything destructive or irreversible (force push, hard
  reset, deleting files, rewriting history).
- Keep commits small with clear messages describing what changed and why.
## Current status
 
Phase 0 — setup. Repo cloned and open in VS Code. README and .gitignore exist.
Next: confirm Python + libraries are installed (Step 0.1), create the `data/`
folder and `explore.py` (Step 1.1 scratch script to inspect yfinance output).
