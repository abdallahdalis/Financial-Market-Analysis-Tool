# Financial Market Analysis Tool

A Python tool for storing and analyzing stock market data — SQLite for storage,
pandas/statsmodels for time-series analytics, and Matplotlib for visualization.

Originally an MCS 275 (Spring 2024) project by Abdallah Dalis; since extended
with a time-series analysis layer (technical indicators, risk-return statistics,
and an ARIMA price forecast).

📄 **Project writeup:** [project4.pdf](project4.pdf)

## Features

- **CRUD** over an OHLCV stock table (insert / update / delete / view) in SQLite.
- **Technical indicators** — SMA(20/50), EMA(20), Bollinger bands, daily & log
  returns, cumulative return, and annualized rolling volatility.
- **Risk–return summary** — total & annualized return, annualized volatility,
  Sharpe ratio, and maximum drawdown.
- **Forecast** — short-horizon close-price forecast via ARIMA(1,1,1)
  (`statsmodels`), with a random-walk-with-drift fallback.
- **Overview chart** — close price with high–low range bars, moving averages,
  Bollinger band, the forecast, and a volume sub-panel.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python seed_demo.py     # populate ~1 trading year of demo data (AAPL, MSFT, TSLA)
python project4.py      # launch the interactive tool
```

Menu:

```
1. View Stock Chart (price, moving averages, Bollinger, volume)
2. Insert Stock Data
3. Update Stock Data
4. Delete Stock Data
5. Analyze (time-series stats + forecast)
6. Exit
```

Example analysis output:

```
=== AAPL — time-series summary ===
  Observations:           252 (2025-06-26 → 2026-06-12)
  Total return:           +57.9%
  Annualized return:      +62.0%
  Annualized volatility:  22.0%
  Sharpe ratio (rf=0):    2.82
  Max drawdown:           -8.3%

  5-day close forecast:
    2026-06-15  289.4
    ...
```

## Project layout

- **`project4.py`** — interactive CLI (menu, CRUD, calls into the analysis layer)
- **`analysis.py`** — time-series functions: `load_prices`, `add_indicators`, `summary_stats`, `forecast`, `analyze`
- **`plotting.py`** — the Matplotlib overview chart
- **`seed_demo.py`** — generates realistic demo OHLCV via geometric Brownian motion
- **`stocks.db`** — SQLite database

## Notes & credits

The demo data is synthetic (GBM), used so the indicators and forecast have
enough history to be meaningful — it is not real market data. The original
class project handled CRUD and basic line/bar charts; the analytics layer,
charting, and forecast were added in the extension.
