# explore.py
# Phase 1, Step 1.1 — a scratch script to SEE what yfinance returns.
# It prints, it doesn't save. The point is to inspect the shape of the
# data and learn the column names before automating the real pull later.

import yfinance as yf

# A Ticker object is a "handle" to everything Yahoo Finance knows about one company.
stock = yf.Ticker("AAPL")

# .info is a big dictionary of stats. .get() returns blank instead of crashing
# if a field is missing. Pull two we'll need later for the DCF:
print("Market cap:", stock.info.get("marketCap"))
print("Beta:", stock.info.get("beta"))

# The three financial statements, each a table with years across the top:
print("\n--- INCOME STATEMENT ---")
print(stock.financials)

print("\n--- BALANCE SHEET ---")
print(stock.balance_sheet)

print("\n--- CASH FLOW ---")
print(stock.cashflow)

# Price history: 5 years of daily open/high/low/close/volume. .tail() = last few rows.
print("\n--- RECENT PRICES ---")
print(stock.history(period="5y").tail())
