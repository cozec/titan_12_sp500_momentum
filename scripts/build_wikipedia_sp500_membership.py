"""Build an approximate point-in-time S&P 500 membership file from Wikipedia.

This is a research-grade bootstrap, not institutional point-in-time data. It
starts with Wikipedia's current S&P 500 constituents, then walks the
"Selected changes" table backward to infer historical membership intervals.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.membership import MEMBERSHIP_COLUMNS, WIKIPEDIA_SP500_URL
from src.utils import normalize_ticker


DEFAULT_OUTPUT = Path("data/sp500_membership_wikipedia_history.csv")


@dataclass
class Interval:
    """One inferred S&P 500 membership interval."""

    ticker: str
    company_name: str
    start_date: pd.Timestamp | pd.NaT
    end_date: pd.Timestamp | pd.NaT
    sector: str = "Unknown"
    source: str = WIKIPEDIA_SP500_URL
    notes: str = (
        "Approximate interval inferred from Wikipedia current constituents and "
        "Selected changes table; validate before production use."
    )


def _clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _clean_ticker(value: object) -> str:
    text = _clean_text(value)
    return normalize_ticker(text) if text else ""


def _load_wikipedia_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    response = requests.get(
        WIKIPEDIA_SP500_URL,
        headers={"User-Agent": "Titan-12 Momentum Rotation research script"},
        timeout=30,
    )
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    if len(tables) < 2:
        raise RuntimeError("Wikipedia S&P 500 page did not expose the expected tables.")
    return tables[0], tables[1]


def _current_intervals(current: pd.DataFrame) -> tuple[list[Interval], dict[str, Interval]]:
    intervals: list[Interval] = []
    active: dict[str, Interval] = {}
    for _, row in current.iterrows():
        ticker = _clean_ticker(row["Symbol"])
        if not ticker:
            continue
        interval = Interval(
            ticker=ticker,
            company_name=_clean_text(row["Security"]),
            start_date=pd.to_datetime(row["Date added"], errors="coerce"),
            end_date=pd.NaT,
            sector=_clean_text(row["GICS Sector"]) or "Unknown",
            notes=(
                "Current Wikipedia constituent; start_date from Wikipedia Date added. "
                "Historical interval adjusted where the Selected changes table "
                "contains a matching add event."
            ),
        )
        intervals.append(interval)
        active[ticker] = interval
    return intervals, active


def _flatten_changes(changes: pd.DataFrame) -> pd.DataFrame:
    if isinstance(changes.columns, pd.MultiIndex):
        changes = changes.copy()
        changes.columns = [
            "_".join(str(part) for part in col if str(part) != "nan").strip("_")
            for col in changes.columns
        ]
    return changes.rename(
        columns={
            "Effective Date_Effective Date": "effective_date",
            "Added_Ticker": "added_ticker",
            "Added_Security": "added_security",
            "Removed_Ticker": "removed_ticker",
            "Removed_Security": "removed_security",
            "Reason_Reason": "reason",
        }
    )


def build_membership() -> pd.DataFrame:
    """Build an approximate membership dataframe in the project schema."""

    current, changes = _load_wikipedia_tables()
    intervals, active = _current_intervals(current)
    sector_by_ticker = {
        interval.ticker: interval.sector
        for interval in intervals
        if interval.sector and interval.sector != "Unknown"
    }

    changes = _flatten_changes(changes)
    changes["effective_date"] = pd.to_datetime(changes["effective_date"], errors="coerce")
    changes = changes.dropna(subset=["effective_date"]).sort_values(
        "effective_date", ascending=False
    )

    for _, row in changes.iterrows():
        effective_date = pd.Timestamp(row["effective_date"]).normalize()
        added_ticker = _clean_ticker(row.get("added_ticker"))
        removed_ticker = _clean_ticker(row.get("removed_ticker"))
        reason = _clean_text(row.get("reason"))

        if added_ticker and added_ticker in active:
            active[added_ticker].start_date = effective_date
            active.pop(added_ticker, None)

        if removed_ticker:
            company_name = _clean_text(row.get("removed_security")) or removed_ticker
            interval = Interval(
                ticker=removed_ticker,
                company_name=company_name,
                start_date=pd.NaT,
                end_date=effective_date - pd.Timedelta(days=1),
                sector=sector_by_ticker.get(removed_ticker, "Unknown"),
                notes=(
                    "Removed according to Wikipedia Selected changes table. "
                    f"Reason: {reason}"
                ).strip(),
            )
            intervals.append(interval)
            active[removed_ticker] = interval

    rows = []
    for interval in intervals:
        rows.append(
            {
                "ticker": interval.ticker,
                "company_name": interval.company_name,
                "start_date": (
                    ""
                    if pd.isna(interval.start_date)
                    else pd.Timestamp(interval.start_date).strftime("%Y-%m-%d")
                ),
                "end_date": (
                    ""
                    if pd.isna(interval.end_date)
                    else pd.Timestamp(interval.end_date).strftime("%Y-%m-%d")
                ),
                "sector": interval.sector or "Unknown",
                "source": interval.source,
                "notes": interval.notes,
            }
        )

    membership = pd.DataFrame(rows, columns=MEMBERSHIP_COLUMNS)
    membership = membership.drop_duplicates(["ticker", "start_date", "end_date"])
    return membership.sort_values(["ticker", "start_date", "end_date"]).reset_index(drop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build approximate historical S&P 500 membership from Wikipedia."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV path to write. Defaults to {DEFAULT_OUTPUT}.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    membership = build_membership()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    membership.to_csv(args.output, index=False)
    removed = membership["end_date"].astype(str).ne("").sum()
    unknown_starts = membership["start_date"].astype(str).eq("").sum()
    print(f"Wrote {len(membership):,} membership intervals to {args.output}")
    print(f"Rows with removal dates: {removed:,}")
    print(f"Rows with unknown start dates: {unknown_starts:,}")
    print("Review this file before replacing data/sp500_membership.csv.")


if __name__ == "__main__":
    main()
