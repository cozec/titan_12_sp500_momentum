"""Command-line entry point for Titan-12 Momentum Rotation."""

from __future__ import annotations

import argparse

from src.backtest import run_backtest
from src.config import BacktestConfig


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for a backtest run."""

    parser = argparse.ArgumentParser(description="Run Titan-12 Momentum Rotation.")
    parser.add_argument("--start-date", default=BacktestConfig.start_date)
    parser.add_argument("--end-date", default=BacktestConfig.end_date)
    parser.add_argument("--top-n", type=int, default=BacktestConfig.top_n)
    parser.add_argument("--benchmark", default=BacktestConfig.benchmark)
    parser.add_argument(
        "--transaction-cost-bps",
        type=float,
        default=BacktestConfig.transaction_cost_bps,
    )
    parser.add_argument("--slippage-bps", type=float, default=BacktestConfig.slippage_bps)
    parser.add_argument(
        "--membership-mode",
        choices=["historical_constituents", "current_constituents"],
        default="historical_constituents",
    )
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Redownload market data instead of using cached CSV files.",
    )
    parser.add_argument(
        "--include-gspc",
        action="store_true",
        help="Also cache ^GSPC data for optional research.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the CLI."""

    args = parse_args()
    config = BacktestConfig(
        start_date=args.start_date,
        end_date=args.end_date,
        top_n=args.top_n,
        benchmark=args.benchmark,
        transaction_cost_bps=args.transaction_cost_bps,
        slippage_bps=args.slippage_bps,
        use_historical_membership=args.membership_mode == "historical_constituents",
        refresh_data=args.refresh_data,
        include_gspc=args.include_gspc,
    )
    results = run_backtest(config)
    stats = results["summary_stats"]
    if not stats.empty:
        print(stats.to_string(index=False))
    print("Wrote outputs to outputs/ and summary.md")


if __name__ == "__main__":
    main()
