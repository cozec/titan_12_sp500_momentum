# Titan-12 Momentum Rotation

Titan-12 Momentum Rotation is a monthly S&P 500 rotation backtest. On the first
trading day of each month, it ranks eligible S&P 500 stocks by a weighted
12-month momentum score, buys the top 3 names at equal weight, and holds them
until the next monthly rebalance.

The score uses only the previous 12 completed monthly returns:

```text
score = 1*r_1 + 2*r_2 + ... + 12*r_12
```

The newest completed month receives the largest weight. The current partial
month is never used for signal calculation.

## Current Research Snapshot

The latest local run used current S&P 500 constituents from Wikipedia. That is
useful for a first pass, but it is survivorship-biased and should not be treated
as point-in-time institutional research.

Latest headline results are documented in `summary.md`:

- strategy final value: $1,413,882 from $100,000
- SPY final value: $366,701 from $100,000
- strategy CAGR: 33.16%
- SPY CAGR: 15.08%
- completed rebalances: 111

The summary also includes:

- run configuration
- headline results
- latest completed basket
- current open basket
- top-3 selections over the past year
- Nasdaq-overlap-excluded top-3 selections

## Setup

Create and activate the project virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running a Backtest

For serious research, provide `data/sp500_membership.csv` with point-in-time
membership history and run:

```bash
python main.py --start-date 2016-01-01 --end-date 2026-05-12
```

To bootstrap from the current S&P 500 list, run:

```bash
python main.py --membership-mode current_constituents
```

That mode is survivorship-biased for historical testing because it uses today's
index members for the full past period.

## Nasdaq-Overlap Exclusion Overlay

For cross-project diversification against the sister Nasdaq strategy, the
research summary includes an optional overlay:

1. Read Nasdaq top-3 picks from
   `/Users/adam/project/momentum_6m/nasdaq100_momentum_backtest/outputs/monthly_selections.csv`.
2. For each matching S&P 500 rebalance date, skip any S&P 500 Titan-12 ticker
   that also appears in the Nasdaq top 3.
3. Backfill from the next-highest S&P 500 Titan-12 ranked names until 3 names
   are selected.

This overlay is reported separately as `Nasdaq-Overlap-Excluded Top 3` in
`summary.md`; it does not replace the baseline backtest results unless promoted
into the execution logic.

Useful CLI options:

```bash
python main.py \
  --start-date 2010-01-01 \
  --end-date 2026-12-31 \
  --top-n 3 \
  --benchmark SPY \
  --transaction-cost-bps 5 \
  --slippage-bps 5 \
  --membership-mode historical_constituents \
  --refresh-data
```

## Membership Data

The membership file must be:

```text
data/sp500_membership.csv
```

Required columns:

```text
ticker,company_name,start_date,end_date,sector,source,notes
```

Rows with missing `start_date` are treated as eligible from the beginning of the
backtest. Rows with missing `end_date` are treated as active.

Historical membership matters because the current S&P 500 excludes companies
that were removed, acquired, or failed. Using only current constituents usually
overstates historical performance.

## Outputs

The backtest writes:

- `outputs/monthly_selections.csv`
- `outputs/portfolio_returns.csv`
- `outputs/summary_stats.csv`
- `outputs/charts/*.png`
- `logs/data_quality_report.csv`
- `logs/backtest.log`
- `summary.md`

The data quality report logs failed downloads, missing adjusted closes,
insufficient history, missing prices, and incomplete selections.

Key charts include the equity curve, drawdown curve, rolling returns, selection
frequency, sector exposure, excess return vs SPY, and a recent-rebalances card
chart showing the latest 12 completed top-3 baskets plus the current open MTD
basket.

## Tests

Run:

```bash
source .venv/bin/activate
pytest
```

The tests cover monthly return calculation, no-lookahead scoring, top-N
selection, first trading day generation, portfolio returns, turnover,
membership filtering, and summary metrics.

## Limitations

This is a research tool, not trading advice. Important limitations include:

- survivorship bias if current constituents are used
- imperfect historical ticker and delisting support
- Yahoo Finance data quality constraints
- taxes are not modeled
- liquidity constraints are not modeled
- execution uses adjusted close on rebalance dates
- transaction cost and slippage assumptions are simplified
- concentrated top-3 portfolios can have high idiosyncratic risk
