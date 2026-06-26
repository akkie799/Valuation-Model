import yfinance as yf
import pandas as pd
import time

tickers = ["AAPL", "MSFT", "NKE", "CMG", "KO"]

rows = []
for t in tickers:
    try:
        s = yf.Ticker(t)
        info = s.info
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
        print(f"  pulled {t}")
    except Exception as e:
        print(f"  skipped {t}: {e}")
    time.sleep(1)

df = pd.DataFrame(rows)
df.to_csv("data/universe.csv", index=False)
print(f"\ndone — {len(df)} tickers written to data/universe.csv")
