"""Shared utility helpers for logging, dates, files, and tabular outputs."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


def setup_logging(log_path: Path) -> None:
    """Configure console and file logging for a backtest run."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def normalize_ticker(ticker: str) -> str:
    """Normalize a ticker for Yahoo Finance while preserving readable symbols."""

    return str(ticker).strip().upper().replace(".", "-")


def save_csv(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    """Save a dataframe to CSV after creating its parent directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def append_quality_issue(
    issues: list[dict[str, object]],
    ticker: str,
    issue_type: str,
    message: str,
    date: object | None = None,
) -> None:
    """Append a normalized data quality issue record to a mutable list."""

    issues.append(
        {
            "date": "" if date is None else pd.Timestamp(date).date().isoformat(),
            "ticker": ticker,
            "issue_type": issue_type,
            "message": message,
        }
    )


def write_summary_markdown(
    path: Path,
    config: object,
    summary_stats: pd.DataFrame,
    portfolio_returns: pd.DataFrame,
    monthly_selections: pd.DataFrame,
    data_quality: pd.DataFrame,
    test_results: str = "Not run by backtest command.",
) -> None:
    """Write a human-readable run summary to markdown."""

    path.parent.mkdir(parents=True, exist_ok=True)
    bias_warning = ""
    if getattr(config, "membership_mode", "") == "current_constituents":
        bias_warning = (
            "\n> WARNING: This run used current S&P 500 constituents and is "
            "survivorship-biased.\n"
        )

    latest_rebalance = "No completed rebalance."
    current_basket = "No current basket."
    if not monthly_selections.empty:
        latest_date = monthly_selections["rebalance_date"].max()
        latest_rows = monthly_selections[
            monthly_selections["rebalance_date"] == latest_date
        ].copy()
        tickers = ", ".join(latest_rows["ticker"].astype(str).tolist())
        latest_rebalance = f"{latest_date}: {tickers}"
        current_basket = tickers

    trades_section = ""
    if len(monthly_selections) < 30 and not monthly_selections.empty:
        trades_section = "\n## Trade Details\n\n"
        trades_section += monthly_selections.to_markdown(index=False)
        trades_section += "\n"

    stats_section = "No summary statistics generated."
    if not summary_stats.empty:
        stats_section = summary_stats.to_markdown(index=False)

    quality_section = "No data quality warnings."
    if not data_quality.empty:
        quality_section = data_quality.head(50).to_markdown(index=False)

    config_rows = {
        "start_date": getattr(config, "start_date", ""),
        "end_date": getattr(config, "end_date", ""),
        "top_n": getattr(config, "top_n", ""),
        "benchmark": getattr(config, "benchmark", ""),
        "transaction_cost_bps": getattr(config, "transaction_cost_bps", ""),
        "slippage_bps": getattr(config, "slippage_bps", ""),
        "membership_mode": getattr(config, "membership_mode", ""),
    }
    config_table = pd.DataFrame(
        [{"setting": key, "value": value} for key, value in config_rows.items()]
    ).to_markdown(index=False)

    run_timestamp = pd.Timestamp.now(tz="UTC").isoformat()
    data_freshness = run_timestamp
    if not portfolio_returns.empty:
        data_freshness = str(portfolio_returns["next_rebalance_date"].max())

    content = f"""# Titan-12 Momentum Rotation Summary

Run timestamp: {run_timestamp}

Data freshness timestamp: {data_freshness}

{bias_warning}
## Active Configuration

{config_table}

## Summary Stats

{stats_section}

## Latest Completed Rebalance

{latest_rebalance}

## Current Open Basket

{current_basket}

## Charts

- outputs/charts/equity_curve_vs_spy.png
- outputs/charts/drawdown_curve.png
- outputs/charts/monthly_return_distribution.png
- outputs/charts/rolling_6_month_return.png
- outputs/charts/rolling_12_month_return.png
- outputs/charts/rolling_sharpe_ratio.png
- outputs/charts/annual_return_bar_chart.png
- outputs/charts/top_selected_stocks_frequency.png
- outputs/charts/sector_exposure_over_time.png
- outputs/charts/excess_return_vs_spy_over_time.png

## Data Quality Notes

{quality_section}

## Test Results

{test_results}
{trades_section}
"""
    path.write_text(content, encoding="utf-8")
