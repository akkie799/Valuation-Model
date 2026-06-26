# Valuation Engine — Full Build Guide

A step-by-step plan to build one connected Excel workbook that you point at any stock and get a real answer from. Four stages: **Screen → Score → Value → Size**, all driven by a single ticker cell and fed by a Python data script.

This guide is written to *teach*, not just instruct. Every step has three parts:

- **Do** — the action.  
- **Why** — the concept you're learning and why it matters.  
- **Check** — how to know you got it right before moving on.

Work through it in order. Don't skip the checkpoints; a model that silently breaks early is the hardest kind to fix later.

---

## Phase 0 — Setup

### Step 0.1 — Tools on your machine

**Do:** Install Python (3.11+) and VS Code if you don't have them. In a terminal, run:

pip install yfinance pandas

**Why:** `yfinance` pulls the data; `pandas` is the table library that holds and reshapes it. These two are your entire data toolkit to start. **Check:** `python -c "import yfinance, pandas; print('ok')"` prints `ok`.

### Step 0.2 — Folder structure

**Do:** Make one project folder, e.g. `valuation-engine/`, with a `data/` subfolder inside it. Your script lives in the root, your CSV outputs go in `data/`. **Why:** A clean folder means Power Query always knows where to find the CSV. Moving files around later breaks the link. **Check:** You can see `valuation-engine/data/` on disk.

### Step 0.3 — Claude Project \+ skills

**Do:** Turn on Code Execution and File Creation (Settings → Capabilities), toggle the **xlsx** skill (Customize → Skills), and create the Claude Project with the custom instructions and this guide uploaded. **Why:** This gives you a tutor that already knows your plan and can generate or fix an Excel tab on demand without you re-explaining context. **Check:** Asking the project "what are we building and what's step 1.1?" returns an answer grounded in this guide.

---

## Phase 1 — The data pipeline (your foundation)

You build the data source first. Everything else reads from it.

### Step 1.1 — Pull one company by hand (learn the library)

**Do:** In a Python file, run:

import yfinance as yf

stock \= yf.Ticker("AAPL")

print(stock.info\["marketCap"\], stock.info\["beta"\])

print(stock.financials)       \# income statement

print(stock.balance\_sheet)    \# balance sheet

print(stock.cashflow)         \# cash flow statement

hist \= stock.history(period="5y")

print(hist.tail())            \# last few days of prices

**Why:** Before automating, you need to *see* what each call returns and what the columns are named. Yahoo's labels (e.g. `Total Revenue`, `Net Income`, `Operating Cash Flow`) are exactly what you'll reference later. **Check:** You can find revenue, net income, total assets, and total debt in the printed tables and know which call each comes from.

### Step 1.2 — Decide your two data zones

**Do:** Plan for two outputs:

1. `universe.csv` — one row per ticker, \~20 columns of metrics (powers Screener \+ most of Scorecard).  
2. `statements_<TICKER>.csv` — full multi-year statements for the *one* company you're deep-diving (powers the DCF). **Why:** The screener needs breadth (many companies, few numbers each); the DCF needs depth (one company, full history). Holding full statements for 500 names is wasteful and slow. Splitting them is the key architectural decision. **Check:** You can state, for each of the four modules, which file it will read from.

### Step 1.3 — Write the universe script

**Do:** Loop over a ticker list, pull the fields you need, and write one tidy row each. Skeleton:

import yfinance as yf, pandas as pd, time

tickers \= \["AAPL", "MSFT", "NKE", "CMG", "KO"\]  \# start small

rows \= \[\]

for t in tickers:

    try:

        s \= yf.Ticker(t)

        info \= s.info

        rows.append({

            "Ticker": t,

            "MarketCap": info.get("marketCap"),

            "Beta": info.get("beta"),

            "PE": info.get("trailingPE"),

            "EVtoEBITDA": info.get("enterpriseToEbitda"),

            "ROE": info.get("returnOnEquity"),

            "ProfitMargin": info.get("profitMargins"),

            "DebtToEquity": info.get("debtToEquity"),

            "RevenueGrowth": info.get("revenueGrowth"),

        })

    except Exception as e:

        print(f"skipped {t}: {e}")

    time.sleep(1)   \# be polite to Yahoo

pd.DataFrame(rows).to\_csv("data/universe.csv", index=False)

print("done")

**Why:** The `try/except` means one bad ticker doesn't kill the whole run — this is what makes it "constantly work." `time.sleep(1)` avoids rate limits. `.get()` returns blank instead of crashing when a field is missing. **Check:** `data/universe.csv` opens and has one clean row per ticker.

### Step 1.4 — Write the statements script

**Do:** For your deep-dive company, export the three statements to CSV (e.g. concatenate revenue, EBIT, D\&A, CapEx, change in working capital, total debt, cash, shares outstanding across the last 4–5 years). **Why:** The DCF needs a *time series* of these line items to project forward. You're building the raw material for free cash flow. **Check:** You can read 4–5 years of revenue and operating cash flow out of the file.

### Step 1.5 — Establish the refresh habit

**Do:** Re-run both scripts whenever you want fresh numbers. Later, point Excel Power Query at these CSVs (Data → Get Data → From Text/CSV) so one Refresh updates the workbook. **Why:** This closes the loop: *run script → refresh Excel → every tab recalculates.* The whole "use it every time" promise depends on this being one button, not an afternoon of copy-paste. **Check:** Changing a ticker in the script and re-running visibly changes the CSV.

---

## Phase 2 — Workbook skeleton

### Step 2.1 — Create the six tabs

**Do:** New workbook, six sheets in this order: `Dashboard`, `Data`, `Screener`, `Scorecard`, `Valuation`, `Sizing`. **Why:** Order \= reading order. The Dashboard is first because it's the one sheet anyone (including an interviewer) needs to see. **Check:** Six tabs, named exactly, no spaces issues.

### Step 2.2 — The master switch

**Do:** On `Dashboard`, pick one cell for the ticker. Select it, and in the Name Box (top-left) type `ctrl_Ticker` and Enter. Now that cell has a name. **Why:** This single named cell drives the entire workbook. Every module will reference `ctrl_Ticker`, so changing it once recalculates everything. Named ranges (not `A1`) make formulas read in English. **Check:** Typing `=ctrl_Ticker` in any blank cell returns whatever you typed in that cell.

### Step 2.3 — Load the data

**Do:** Import `universe.csv` into `Data` via Power Query, then convert it to a Table (Ctrl+T) named `tblUniverse`. Do the same for the statements file as `tblStatements`. **Why:** Tables are *dynamic* — formulas like `tblUniverse[ROE]` auto-expand when rows are added, and they survive a data refresh. This is what keeps the model from breaking every time the data changes. **Check:** `=ROWS(tblUniverse)` returns your ticker count.

### Step 2.4 — Adopt the color convention

**Do:** From now on: **blue font \= hardcoded inputs**, **black \= formulas**, **green \= links to other sheets**. **Why:** It costs nothing and instantly signals to any reviewer that you build models the professional way. It also helps *you* never accidentally type over a formula. **Check:** Your `ctrl_Ticker` input cell is blue.

---

## Phase 3 — Screener (idea generation)

Goal: rank a universe fairly so the best candidates float to the top.

### Step 3.1 — Pull the factors

**Do:** On `Screener`, reference the columns you'll score: value (low `EVtoEBITDA`, low `PE`), quality (`ROE`, `ProfitMargin`), growth (`RevenueGrowth`), and a leverage penalty (`DebtToEquity`). **Why:** These are *factors* — characteristics that academically tend to relate to returns. You're encoding an investing philosophy in numbers. **Check:** Each factor column is populated for every ticker.

### Step 3.2 — Put factors on the same scale (z-scores)

**Do:** For each factor column, compute a z-score per company: `=STANDARDIZE(value, AVERAGE(column), STDEV.P(column))`. For "lower is better" factors (P/E, EV/EBITDA, debt), multiply the z-score by \-1 so high score always \= good. **Why:** This is the core statistics lesson. Companies report wildly different raw numbers; a z-score says "how many standard deviations above or below the group average is this?" Now a P/E and a growth rate are comparable on one ruler. **Check:** Each z-score column averages \~0 across the universe.

### Step 3.3 — Composite score and rank

**Do:** Weight the z-scores (e.g. 40% value, 35% quality, 25% growth) with `SUMPRODUCT`, then `=RANK(...)` or `=PERCENTRANK(...)` the composite. **Why:** Weighting is where *your* judgment enters — a value investor weights value heavily, a growth investor doesn't. The composite turns many signals into one decision-ready number. **Check:** Sorting by composite produces an intuitive ordering (cheap, profitable, growing names near the top).

### Step 3.4 — Hand the winner to the workbook

**Do:** Add a cell where you type a chosen ticker, or a formula that grabs the top-ranked one, and have it feed `ctrl_Ticker` (or just copy it there). **Why:** This is the hand-off from "scan the field" to "deep-dive one name." It connects stage 1 to stages 2–4. **Check:** Picking a name updates `ctrl_Ticker` and the other tabs react.

---

## Phase 4 — Scorecard (the quality \+ safety filter)

Goal: catch value traps, fragile balance sheets, and accounting red flags before you fall in love with a story. Build the active company's row with `=XLOOKUP(ctrl_Ticker, tblUniverse[Ticker], tblUniverse[...])` plus a few statement items.

### Step 4.1 — Piotroski F-Score (0–9)

**Do:** Nine binary tests, each scoring 1 if true. Profitability: net income \> 0; operating cash flow \> 0; ROA improved vs last year; operating cash flow \> net income. Leverage/liquidity: long-term debt ratio fell; current ratio rose; no new shares issued. Efficiency: gross margin rose; asset turnover rose. Sum them. **Why:** It's a *quality* checklist invented by an accounting professor. A high F-Score (8–9) means a fundamentally improving business; a low one (0–2) is a warning. The "operating cash flow \> net income" test is the gem — it flags earnings that aren't backed by real cash. **Check:** Each test returns a clean 1 or 0; total is 0–9.

### Step 4.2 — Altman Z-Score (bankruptcy risk)

**Do:** `Z = 1.2·X1 + 1.4·X2 + 3.3·X3 + 0.6·X4 + 1.0·X5`, where X1 \= working capital/total assets, X2 \= retained earnings/total assets, X3 \= EBIT/total assets, X4 \= market value of equity/total liabilities, X5 \= sales/total assets. **Why:** It compresses five solvency signals into one distress score. Above 2.99 \= safe, 1.81–2.99 \= grey zone, below 1.81 \= distress risk. (Note: this is the original manufacturing version; there's a Z'' variant for non-manufacturers — worth knowing the model has limits.) **Check:** Z lands in a sensible range for a healthy company you test (well above 3).

### Step 4.3 — Beneish M-Score (stretch goal — manipulation flag)

**Do:** An 8-variable model comparing this year to last (sales/receivables, gross margin, asset quality, sales growth, depreciation, SG\&A, leverage, and total accruals). `M > -1.78` suggests possible earnings manipulation. **Why:** This is advanced and needs two years of clean data, so treat it as optional. But understanding *why* each variable hints at manipulation (e.g. receivables growing faster than sales) is a serious analyst skill. **Check:** You can explain in one sentence what each of the 8 variables is testing.

### Step 4.4 — Composite verdict

**Do:** Combine the scores into a single buy / watch / pass flag with `IF` logic, and write it to a fixed output cell. **Why:** Each score answers a different question; the verdict synthesizes them. This is the cell the Dashboard will read. **Check:** A strong company shows green; deliberately feed a weak one and confirm it flags.

---

## Phase 5 — Valuation (DCF \+ reverse DCF — the core)

Goal: estimate what the business is actually worth, independent of its price. Reads `tblStatements`.

### Step 5.1 — Build the WACC (your discount rate)

**Do:** Cost of equity via CAPM: `Re = Rf + Beta·ERP` (risk-free rate \+ beta × equity risk premium). Cost of debt after tax: `Rd·(1−tax)`. Blend by weights: `WACC = E/V·Re + D/V·Rd·(1−tax)`. **Why:** WACC is the rate that translates future dollars into today's dollars — it's the price of waiting plus the price of risk. Every assumption (Rf, ERP, beta) is a judgment you must be able to defend in an interview. **Check:** WACC lands in a believable range (most large caps \~7–11%). *Watch the circular-reference trap:* if you weight by market value of equity, enable iterative calculation (File → Options → Formulas) or use target weights.

### Step 5.2 — Project free cash flow

**Do:** For 5 years, build `FCFF = EBIT·(1−tax) + D&A − CapEx − ΔNet Working Capital`, growing the drivers off your statement history and explicit assumptions. **Why:** Free cash flow is the actual cash the business can return to all investors — the thing being valued. Building it from the statements teaches you how the three statements connect. **Check:** Year-1 FCF is in the same ballpark as recent historical FCF.

### Step 5.3 — Terminal value and intrinsic value

**Do:** Terminal value via Gordon Growth: `TV = FCF₅·(1+g)/(WACC−g)` (and cross-check with an EV/EBITDA exit multiple). Discount all FCFs and the TV at WACC with `XNPV`. Sum to Enterprise Value, subtract net debt for Equity Value, divide by shares for value per share. **Why:** Most of a DCF's value usually sits in the terminal value, so the long-run growth assumption `g` matters enormously — keep it below long-run GDP growth or you're implying the company outgrows the economy forever. **Check:** Intrinsic value per share is a sane number; compare your two terminal-value methods — large divergence means an assumption is off.

### Step 5.4 — Margin of safety

**Do:** `Margin of Safety = (Intrinsic Value − Price) / Intrinsic Value`. Pull current price from your data. **Why:** This is the buffer between what you pay and what it's worth — your protection against being wrong. A big positive margin is the whole point of value investing. **Check:** A stock trading near your intrinsic estimate shows a small margin; a cheap one shows a large positive margin.

### Step 5.5 — Reverse DCF (the mind-shift)

**Do:** Set up the model so you can input the *current price* and use Goal Seek (Data → What-If → Goal Seek) to solve for the growth rate that makes intrinsic value equal price. **Why:** This flips the question from "what's it worth?" to "what is the market already assuming, and is that beatable?" It turns you from a number-guesser into a thesis-tester. Note Goal Seek is a manual action, not a live formula — so either press it to refresh, or solve algebraically. **Check:** The implied growth rate it returns is one you can argue is either realistic or too optimistic.

---

## Phase 6 — Sizing (the decision layer)

Goal: turn "this looks undervalued" into "buy this much." Reads the valuation output plus your scenario inputs.

### Step 6.1 — Scenarios

**Do:** Define bull / base / bear cases, each with a target price and a probability that sums to 100%. **Why:** This is where research and intuition formally enter the math. You're admitting the future is uncertain and quantifying your own conviction. **Check:** Probabilities sum to exactly 1\.

### Step 6.2 — Probability-weighted expected return

**Do:** `Expected Return = SUMPRODUCT(probabilities, scenario returns)`. **Why:** One number that blends upside, downside, and your confidence. This is expected-value thinking — the foundation of every good bet. **Check:** Moving probability toward the bear case lowers expected return.

### Step 6.3 — Position size (fractional Kelly)

**Do:** Compute the Kelly fraction from your edge and odds, then take a fraction of it (¼ Kelly is common) and cap it at a sane max (e.g. 10%). **Why:** Full Kelly maximizes long-run growth but is wildly volatile; fractional Kelly captures most of the benefit with far less risk of ruin. This is risk management as math, not vibes. **Check:** Higher conviction → larger suggested size, but never an absurd all-in number.

---

## Phase 7 — Dashboard (the cockpit)

### Step 7.1 — Pull the headlines

**Do:** On `Dashboard`, link to each module's output cell: screener rank, composite score, intrinsic value, margin of safety, recommended size — ending in one buy / watch / pass flag. **Why:** The Dashboard does no calculating; it only displays. One-directional flow (Data → modules → Dashboard) keeps the model auditable. **Check:** Changing `ctrl_Ticker` updates every Dashboard figure at once.

### Step 7.2 — Make it readable at a glance

**Do:** Conditional formatting (green/amber/red) on the verdict and margin of safety; a clean layout with labels. **Why:** This is the screenshot that goes in your portfolio and the screen you'll show in an interview. Presentation is part of the deliverable. **Check:** A non-finance friend can look at it and tell whether the verdict is buy or pass.

---

## Phase 8 — Polish and tell the story

### Step 8.1 — Stress-test it

**Do:** Run 5–10 companies you have a view on. Where the model disagrees with your gut, dig into *why* — usually it teaches you something. **Why:** A model you can't poke holes in is a model you don't understand. This is also exactly how interviewers will probe it.

### Step 8.2 — Document your assumptions

**Do:** Add an `Assumptions` note (Rf, ERP, tax rate, weighting choices) with one line defending each. **Why:** Defensible assumptions are the difference between a real analyst and someone who typed numbers. This page is interview gold.

### Step 8.3 — Write it up

**Do:** Draft the LinkedIn post and a one-line resume bullet *after* it works. Keep specifics honest to what you actually built. **Why:** The artifact gets you the interview; the story gets you through it. Write about what exists, never about what you intend to build.

---

## The connective-tissue rules (keep these visible)

- One named input cell (`ctrl_Ticker`) drives everything.  
- Reference data with named ranges and `XLOOKUP`, never raw cell addresses.  
- Each module writes to a fixed output block; the Dashboard only links to those.  
- Data flows one direction: Data → modules → Dashboard.  
- Blue \= input, black \= formula, green \= link.  
- Refresh loop: run Python script → Power Query Refresh → workbook recalculates.

## Two gotchas you *will* hit

1. **WACC circular reference** — enable iterative calculation or use target weights.  
2. **Goal Seek isn't live** — the reverse DCF needs a manual Goal Seek (or an algebraic solve / tiny macro) to refresh.

Build in order. Pass each checkpoint. By the end you won't just have a workbook — you'll understand every number in it well enough to defend it cold.  
