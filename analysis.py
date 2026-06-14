"""Time-series analytics for the Financial Market Analysis Tool.

Pure, testable functions: load OHLCV from SQLite into a pandas DataFrame, add
technical / statistical indicators, summarize risk-return, and produce a short
price forecast. Kept separate from the CLI so it can be imported and unit-tested.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def load_prices(conn, symbol: str) -> pd.DataFrame:
    """Load OHLCV rows for a symbol into a date-indexed DataFrame."""
    df = pd.read_sql_query(
        "SELECT date, open, high, low, close, volume "
        "FROM stocks WHERE symbol = ? ORDER BY date",
        conn, params=(symbol,), parse_dates=["date"],
    )
    if df.empty:
        return df
    return df.set_index("date")


def add_indicators(df: pd.DataFrame,
                   sma_windows=(20, 50),
                   boll_window=20, boll_k=2.0,
                   vol_window=20) -> pd.DataFrame:
    """Append technical / statistical indicators to an OHLCV frame."""
    out = df.copy()
    out["daily_return"] = out["close"].pct_change()
    out["cum_return"] = (1 + out["daily_return"]).cumprod() - 1
    out["log_return"] = np.log(out["close"]).diff()

    for w in sma_windows:
        out[f"sma_{w}"] = out["close"].rolling(w, min_periods=1).mean()
    out["ema_20"] = out["close"].ewm(span=20, adjust=False).mean()

    # Annualized rolling volatility (std of daily returns scaled by sqrt(252))
    out["roll_vol"] = out["daily_return"].rolling(vol_window, min_periods=2).std() * np.sqrt(TRADING_DAYS)

    # Bollinger bands around the rolling mean
    mid = out["close"].rolling(boll_window, min_periods=1).mean()
    sd = out["close"].rolling(boll_window, min_periods=1).std(ddof=0)
    out["boll_mid"] = mid
    out["boll_upper"] = mid + boll_k * sd
    out["boll_lower"] = mid - boll_k * sd
    return out


def summary_stats(df: pd.DataFrame) -> dict:
    """Risk-return summary for a symbol's price history."""
    r = df["close"].pct_change().dropna()
    if r.empty:
        return {}
    total_return = df["close"].iloc[-1] / df["close"].iloc[0] - 1
    ann_return = (1 + r.mean()) ** TRADING_DAYS - 1
    ann_vol = r.std() * np.sqrt(TRADING_DAYS)
    sharpe = ann_return / ann_vol if ann_vol else float("nan")
    # Max drawdown
    curve = (1 + r).cumprod()
    drawdown = (curve / curve.cummax() - 1).min()
    return {
        "observations": int(df.shape[0]),
        "start": df.index[0].date().isoformat(),
        "end": df.index[-1].date().isoformat(),
        "total_return": float(total_return),
        "annualized_return": float(ann_return),
        "annualized_volatility": float(ann_vol),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(drawdown),
    }


def forecast(df: pd.DataFrame, steps: int = 5) -> pd.Series:
    """Short-horizon close-price forecast.

    Uses ARIMA(1,1,1) when statsmodels is available and there is enough data;
    otherwise falls back to a random-walk-with-drift projection so the function
    always returns something usable.
    """
    close = df["close"].astype(float)
    last_date = df.index[-1]
    future_idx = pd.bdate_range(last_date, periods=steps + 1, freq="B")[1:]

    if len(close) >= 10:
        try:
            from statsmodels.tsa.arima.model import ARIMA
            model = ARIMA(close.reset_index(drop=True), order=(1, 1, 1)).fit()
            fc = model.forecast(steps=steps)
            return pd.Series(np.asarray(fc), index=future_idx, name="forecast")
        except Exception:
            pass  # fall through to drift model

    drift = close.diff().mean()
    if np.isnan(drift):
        drift = 0.0
    vals = close.iloc[-1] + drift * np.arange(1, steps + 1)
    return pd.Series(vals, index=future_idx, name="forecast")


def analyze(conn, symbol: str, forecast_steps: int = 5):
    """Return (indicators_df, stats_dict, forecast_series) for a symbol."""
    df = load_prices(conn, symbol)
    if df.empty:
        raise ValueError(f"No data for symbol '{symbol}'.")
    ind = add_indicators(df)
    stats = summary_stats(df)
    fc = forecast(df, steps=forecast_steps)
    return ind, stats, fc
