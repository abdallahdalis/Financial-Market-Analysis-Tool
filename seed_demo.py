"""Populate stocks.db with realistic demo OHLCV data.

Generates ~1 trading year of daily bars per ticker using a geometric Brownian
motion price path, so the analytics (SMA-50, Bollinger, rolling volatility,
ARIMA forecast) have enough history to be meaningful.

    python seed_demo.py            # reseed the default tickers
"""
import sqlite3
from datetime import date, timedelta

import numpy as np

DB = "stocks.db"
TICKERS = {
    "AAPL": (185.0, 0.18, 0.22),   # start price, annual drift, annual vol
    "MSFT": (410.0, 0.20, 0.24),
    "TSLA": (240.0, 0.05, 0.55),
}
DAYS = 252
TRADING_DAYS = 252


def gbm_path(start, mu, sigma, n, rng):
    """Daily geometric Brownian motion closing prices."""
    dt = 1 / TRADING_DAYS
    shocks = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
    return start * np.exp(np.cumsum(shocks))


def business_days(n, end=None):
    """Return the last n business days ending at `end` (default today)."""
    end = end or date.today()
    days, d = [], end
    while len(days) < n:
        if d.weekday() < 5:  # Mon–Fri
            days.append(d)
        d -= timedelta(days=1)
    return list(reversed(days))


def build_rows(symbol, start, mu, sigma, rng):
    close = gbm_path(start, mu, sigma, DAYS, rng)
    dates = business_days(DAYS)
    rows = []
    prev = start
    for d, c in zip(dates, close):
        o = prev
        hi = max(o, c) * (1 + abs(rng.normal(0, 0.004)))
        lo = min(o, c) * (1 - abs(rng.normal(0, 0.004)))
        vol = int(abs(rng.normal(5_000_000, 1_500_000)))
        rows.append((d.isoformat(), symbol, round(o, 2), round(hi, 2),
                     round(lo, 2), round(c, 2), vol))
        prev = c
    return rows


def main():
    rng = np.random.default_rng(275)  # reproducible
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS stocks
                 (date text, symbol text, open real, high real,
                  low real, close real, volume integer)""")
    for sym, (start, mu, sigma) in TICKERS.items():
        c.execute("DELETE FROM stocks WHERE symbol = ?", (sym,))
        rows = build_rows(sym, start, mu, sigma, rng)
        c.executemany(
            "INSERT INTO stocks VALUES (?,?,?,?,?,?,?)", rows)
        print(f"seeded {sym}: {len(rows)} bars "
              f"({rows[0][0]} → {rows[-1][0]})")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
