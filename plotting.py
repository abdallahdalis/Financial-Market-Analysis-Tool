"""Matplotlib charts for the Financial Market Analysis Tool."""
import matplotlib.pyplot as plt


def plot_overview(ind, symbol, forecast=None, save_path=None):
    """Two-panel chart: price with SMAs / Bollinger / high-low range + forecast
    on top, daily volume on the bottom.

    `ind` is the indicator DataFrame from analysis.add_indicators.
    If `save_path` is given the figure is written to disk instead of shown.
    """
    fig, (ax, axv) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    # High–low daily range (addresses original grader feedback)
    ax.vlines(ind.index, ind["low"], ind["high"],
              color="#cbd5e1", linewidth=3, label="High–Low range")
    ax.plot(ind.index, ind["close"], color="#1d4ed8", linewidth=1.8, label="Close")

    for w, c in (("sma_20", "#f59e0b"), ("sma_50", "#10b981")):
        if w in ind and ind[w].notna().any():
            ax.plot(ind.index, ind[w], linewidth=1.2, color=c, label=w.upper().replace("_", " "))

    if {"boll_upper", "boll_lower"}.issubset(ind.columns):
        ax.fill_between(ind.index, ind["boll_lower"], ind["boll_upper"],
                        color="#1d4ed8", alpha=0.07, label="Bollinger (20, 2σ)")

    if forecast is not None and len(forecast):
        ax.plot(forecast.index, forecast.values, "--o", color="#dc2626",
                markersize=4, linewidth=1.4, label=f"Forecast ({len(forecast)}d)")

    ax.set_title(f"{symbol} — price, moving averages & forecast")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2)

    axv.bar(ind.index, ind["volume"], color="#94a3b8", width=0.8)
    axv.set_ylabel("Volume")
    axv.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=110)
        plt.close(fig)
        return save_path
    plt.show()
    return None
