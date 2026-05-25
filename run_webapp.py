"""Run the local Titan-12 dashboard.

Usage:
    python run_webapp.py

By default the app binds to the local loopback host on port 8766. Override with:
    TITAN12_HOST=0.0.0.0 TITAN12_PORT=8766 python run_webapp.py
"""

from __future__ import annotations

import json
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import pandas as pd

from src.config import BacktestConfig
from src.download_data import load_cached_price_data
from src.membership import get_eligible_universe, get_member_metadata, load_sp500_membership
from src.signals import (
    calculate_month_end_prices,
    calculate_monthly_returns,
    calculate_titan12_score,
    prices_to_adj_close_frame,
    rank_stocks_by_score,
)


PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "webapp" / "static"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
DEFAULT_NASDAQ_ROOT = Path(
    "/Users/adam/project/momentum_6m_claude/nasdaq100_momentum_backtest"
)
NASDAQ_SELECTIONS_PATH = Path(
    os.environ.get(
        "NASDAQ_SELECTIONS_PATH",
        DEFAULT_NASDAQ_ROOT / "outputs" / "monthly_selections.csv",
    )
)
NASDAQ_OPEN_PATH = Path(
    os.environ.get(
        "NASDAQ_OPEN_PATH",
        DEFAULT_NASDAQ_ROOT / "outputs" / "open_rebalance_picks.csv",
    )
)


def _safe_float(value: object) -> Optional[float]:
    """Return a JSON-safe float or None."""

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(result):
        return None
    return result


def _row_values(df: pd.DataFrame, date: object) -> list[dict[str, object]]:
    """Return sorted selection rows for one rebalance date."""

    date_rows = df[df["rebalance_date"].eq(date)].sort_values("rank")
    rows = []
    for _, row in date_rows.iterrows():
        rows.append(
            {
                "ticker": row["ticker"],
                "rank": int(row["rank"]),
                "stock_return": _safe_float(row.get("stock_return")),
                "score": _safe_float(row.get("weighted_momentum_score")),
                "sector": row.get("sector", "Unknown"),
            }
        )
    return rows


def _stock_return(adj_close: pd.DataFrame, ticker: str, entry_date: object, exit_date: object) -> Optional[float]:
    """Calculate adjusted-close return for a ticker over a holding period."""

    entry = pd.Timestamp(entry_date).normalize()
    exit_ = pd.Timestamp(exit_date).normalize()
    if ticker not in adj_close.columns or entry not in adj_close.index or exit_ not in adj_close.index:
        return None
    entry_price = adj_close.loc[entry, ticker]
    exit_price = adj_close.loc[exit_, ticker]
    if pd.isna(entry_price) or pd.isna(exit_price) or entry_price <= 0:
        return None
    return float(exit_price / entry_price - 1.0)


def _nasdaq_excluded_history(
    latest_dates: list[pd.Timestamp],
    portfolio: pd.DataFrame,
) -> list[dict[str, object]]:
    """Build recent rebalance history after excluding same-date Nasdaq picks."""

    if not NASDAQ_SELECTIONS_PATH.exists():
        return []

    config = BacktestConfig(end_date="2026-05-17", use_historical_membership=True)
    membership = load_sp500_membership(config.membership_path)
    tickers = sorted(set(membership["ticker"].dropna().tolist() + [config.benchmark]))
    price_data = load_cached_price_data(
        tickers,
        config.raw_price_dir,
        config.start_date,
        config.end_date,
    )
    adj_close = prices_to_adj_close_frame(price_data)
    monthly_returns = calculate_monthly_returns(
        calculate_month_end_prices(adj_close.drop(columns=[config.benchmark], errors="ignore"))
    )
    nasdaq_selections = pd.read_csv(NASDAQ_SELECTIONS_PATH, parse_dates=["rebalance_date"])

    history: list[dict[str, object]] = []
    for date in latest_dates:
        date = pd.Timestamp(date).normalize()
        portfolio_row = portfolio[portfolio["rebalance_date"].eq(date)]
        if portfolio_row.empty:
            continue
        exit_date = pd.Timestamp(portfolio_row["next_rebalance_date"].iloc[0]).normalize()
        excluded = nasdaq_selections[
            nasdaq_selections["rebalance_date"].eq(date)
        ]["ticker"].astype(str).tolist()
        metadata = get_member_metadata(membership, date)
        eligible = get_eligible_universe(membership, date)
        scores = calculate_titan12_score(
            monthly_returns=monthly_returns,
            rebalance_date=date,
            lookback_months=config.lookback_months,
            weights=config.weights,
            eligible_tickers=eligible["ticker"].tolist(),
            metadata=metadata,
        )
        ranked = rank_stocks_by_score(scores)
        adjusted = ranked[~ranked["ticker"].isin(excluded)].head(config.top_n)
        picks: list[dict[str, object]] = []
        for _, row in adjusted.iterrows():
            ticker = row["ticker"]
            picks.append(
                {
                    "ticker": ticker,
                    "rank": int(row["rank"]),
                    "stock_return": _stock_return(adj_close, ticker, date, exit_date),
                    "score": _safe_float(row.get("weighted_momentum_score")),
                    "sector": row.get("sector", "Unknown"),
                }
            )
        portfolio_return = sum(p["stock_return"] or 0 for p in picks) / max(len(picks), 1)
        history.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "label": date.strftime("%b %Y"),
                "excluded": excluded,
                "picks": picks,
                "portfolio_return": portfolio_return,
            }
        )
    return history


def _latest_open() -> list[dict[str, object]]:
    """Load current open picks if the generated file exists."""

    path = OUTPUT_DIR / "open_rebalance_picks.csv"
    if not path.exists():
        path = OUTPUT_DIR / "open_may_2026_selection.csv"
    if not path.exists():
        return []
    open_df = pd.read_csv(path)
    rows = []
    for _, row in open_df.sort_values("rank").iterrows():
        rows.append(
            {
                "ticker": row["ticker"],
                "rank": int(row["rank"]),
                "date": row["rebalance_date"],
                "as_of": row["as_of_date"],
                "entry_price": _safe_float(row.get("entry_price")),
                "latest_price": _safe_float(row.get("as_of_price")),
                "stock_return": _safe_float(row.get("stock_return", row.get("mtd_return"))),
                "score": _safe_float(row.get("weighted_momentum_score")),
            }
        )
    return rows


def _nasdaq_excluded_open() -> dict[str, object]:
    """Return current Nasdaq overlap exclusions and adjusted S&P picks."""

    excluded: list[str] = []
    open_picks = _latest_open()
    open_date = pd.Timestamp(open_picks[0]["date"]).normalize() if open_picks else None
    if NASDAQ_OPEN_PATH.exists():
        ndx_open = pd.read_csv(NASDAQ_OPEN_PATH)
        excluded = ndx_open.sort_values("rank")["ticker"].astype(str).tolist()
    elif NASDAQ_SELECTIONS_PATH.exists() and open_date is not None:
        ndx_selections = pd.read_csv(NASDAQ_SELECTIONS_PATH, parse_dates=["rebalance_date"])
        dates = sorted(
            date
            for date in ndx_selections["rebalance_date"].dropna().unique()
            if pd.Timestamp(date).normalize() <= open_date
        )
        if dates:
            latest_date = dates[-1]
            excluded = (
                ndx_selections[ndx_selections["rebalance_date"].eq(latest_date)]
                .sort_values("rank")["ticker"]
                .astype(str)
                .tolist()
            )
    if not excluded:
        return {"excluded": excluded, "adjusted": open_picks}
    if not open_picks:
        return {"excluded": excluded, "adjusted": []}

    open_date = pd.Timestamp(open_picks[0]["date"]).normalize()
    as_of_date = pd.Timestamp(open_picks[0]["as_of"]).normalize()
    config = BacktestConfig(
        end_date=as_of_date.strftime("%Y-%m-%d"),
        use_historical_membership=True,
    )
    membership = load_sp500_membership(config.membership_path)
    tickers = sorted(set(membership["ticker"].dropna().tolist() + [config.benchmark]))
    price_data = load_cached_price_data(
        tickers,
        config.raw_price_dir,
        config.start_date,
        config.end_date,
    )
    adj_close = prices_to_adj_close_frame(price_data)
    monthly_returns = calculate_monthly_returns(
        calculate_month_end_prices(adj_close.drop(columns=[config.benchmark], errors="ignore"))
    )
    metadata = get_member_metadata(membership, open_date)
    eligible = get_eligible_universe(membership, open_date)
    scores = calculate_titan12_score(
        monthly_returns=monthly_returns,
        rebalance_date=open_date,
        lookback_months=config.lookback_months,
        weights=config.weights,
        eligible_tickers=eligible["ticker"].tolist(),
        metadata=metadata,
    )
    ranked = rank_stocks_by_score(scores)
    adjusted = []
    for _, row in ranked[~ranked["ticker"].isin(excluded)].head(config.top_n).iterrows():
        ticker = row["ticker"]
        adjusted.append(
            {
                "ticker": ticker,
                "rank": int(row["rank"]),
                "date": open_date.strftime("%Y-%m-%d"),
                "as_of": as_of_date.strftime("%Y-%m-%d"),
                "stock_return": _stock_return(adj_close, ticker, open_date, as_of_date),
                "score": _safe_float(row.get("weighted_momentum_score")),
                "sector": row.get("sector", "Unknown"),
            }
        )
    return {"excluded": excluded, "adjusted": adjusted}


def build_dashboard_payload() -> dict[str, object]:
    """Build the JSON payload consumed by the local dashboard."""

    selections = pd.read_csv(OUTPUT_DIR / "monthly_selections.csv", parse_dates=["rebalance_date"])
    portfolio = pd.read_csv(OUTPUT_DIR / "portfolio_returns.csv", parse_dates=["rebalance_date", "next_rebalance_date"])
    stats = pd.read_csv(OUTPUT_DIR / "summary_stats.csv").iloc[0]
    latest_dates = sorted(selections["rebalance_date"].drop_duplicates())[-12:]
    baseline_recent = []
    for date in latest_dates:
        picks = _row_values(selections, date)
        baseline_recent.append(
            {
                "date": pd.Timestamp(date).strftime("%Y-%m-%d"),
                "label": pd.Timestamp(date).strftime("%b %Y"),
                "picks": picks,
                "portfolio_return": sum(p["stock_return"] or 0 for p in picks) / max(len(picks), 1),
            }
        )
    recent = _nasdaq_excluded_history(latest_dates, portfolio) or baseline_recent

    recent_portfolio = portfolio[portfolio["rebalance_date"].isin(latest_dates)]
    open_picks = _latest_open()
    open_return = None
    if open_picks:
        open_return = sum(p["stock_return"] or 0 for p in open_picks) / len(open_picks)

    return {
        "computed_at": pd.Timestamp.now().isoformat(timespec="seconds"),
        "data_freshness": "2026-05-15",
        "bias_warning": "Approximate historical S&P 500 membership from Wikipedia selected changes.",
        "stats": {
            "cagr": _safe_float(stats["CAGR"]),
            "sharpe": _safe_float(stats["Sharpe_ratio"]),
            "max_drawdown": _safe_float(stats["max_drawdown"]),
            "total_return": _safe_float(stats["total_return"]),
            "win_rate_vs_spy": _safe_float(stats["win_rate_vs_SPY"]),
            "average_turnover": _safe_float(stats["average_turnover"]),
            "final_value": _safe_float(portfolio["portfolio_value"].iloc[-1]),
            "spy_value": _safe_float(portfolio["spy_value"].iloc[-1]),
        },
        "window": {
            "first": recent[0]["date"],
            "last": recent[-1]["date"],
            "months": len(recent),
            "strategy_return": _safe_float(pd.Series([r["portfolio_return"] for r in recent]).add(1).prod() - 1),
            "spy_return": _safe_float((1 + recent_portfolio["spy_return"]).prod() - 1),
            "mode": "Nasdaq-overlap-excluded",
        },
        "open": {
            "picks": open_picks,
            "portfolio_return": open_return,
            "date": open_picks[0]["date"] if open_picks else None,
            "as_of": open_picks[0]["as_of"] if open_picks else None,
        },
        "recent": recent,
        "nasdaq_overlay": _nasdaq_excluded_open(),
        "charts": {
            "recent_rebalances": "/charts/recent_rebalances.png",
            "equity_curve": "/charts/equity_curve_vs_spy.png",
            "drawdown": "/charts/drawdown_curve.png",
        },
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve static dashboard files, charts, and JSON API."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        if parsed.path == "/api/dashboard":
            return self._send_json(build_dashboard_payload())
        if parsed.path.startswith("/charts/"):
            chart = CHART_DIR / parsed.path.removeprefix("/charts/")
            return self._send_file(chart)
        return SimpleHTTPRequestHandler.do_GET(self)

    def _send_json(self, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "File not found")
            return
        body = path.read_bytes()
        content_type = "image/png" if path.suffix == ".png" else "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    """Start the local dashboard server."""

    host = os.environ.get("TITAN12_HOST", "127.0.0.1")
    port = int(os.environ.get("TITAN12_PORT", "8766"))
    os.chdir(STATIC_DIR)
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Titan-12 dashboard running on {host}, port {port}.")
    server.serve_forever()


if __name__ == "__main__":
    main()
