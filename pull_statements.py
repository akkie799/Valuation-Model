import yfinance as yf
import pandas as pd

ticker = "AAPL"

s = yf.Ticker(ticker)
inc = s.financials
bs = s.balance_sheet
cf = s.cashflow

# Each line maps a readable label to the exact row name yfinance uses.
# .loc pulls that row; if the name is missing, the except catches it.
items = {
    # Income statement
    "Revenue": ("inc", "Total Revenue"),
    "EBIT": ("inc", "EBIT"),
    "NetIncome": ("inc", "Net Income"),
    "TaxProvision": ("inc", "Tax Provision"),
    # Balance sheet
    "TotalAssets": ("bs", "Total Assets"),
    "TotalDebt": ("bs", "Total Debt"),
    "Cash": ("bs", "Cash And Cash Equivalents"),
    "CurrentAssets": ("bs", "Current Assets"),
    "CurrentLiabilities": ("bs", "Current Liabilities"),
    "SharesOutstanding": ("bs", "Ordinary Shares Number"),
    # Cash flow
    "OperatingCashFlow": ("cf", "Operating Cash Flow"),
    "CapEx": ("cf", "Capital Expenditure"),
    "DepreciationAmortization": ("cf", "Depreciation And Amortization"),
    "ChangeInWorkingCapital": ("cf", "Change In Working Capital"),
}

sources = {"inc": inc, "bs": bs, "cf": cf}

rows = []
for label, (src_key, row_name) in items.items():
    src = sources[src_key]
    try:
        row = src.loc[row_name]
        row.name = label
        rows.append(row)
    except KeyError:
        print(f"  missing: {row_name}")

df = pd.DataFrame(rows)

# Columns are timestamps like 2025-09-30 — simplify to just the year
df.columns = [col.year for col in df.columns]

# Sort columns oldest to newest (left to right) for natural reading
df = df[sorted(df.columns)]

outpath = f"data/statements_{ticker}.csv"
df.to_csv(outpath, index_label="LineItem")
print(f"done — {len(df)} items written to {outpath}")
print(df.to_string())
