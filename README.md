# Titan-12 Momentum Rotation

## Referece:
https://www.xiaohongshu.com/explore/6a01f225000000003700eb1c?app_platform=ios&app_version=9.29&share_from_user_hidden=true&xsec_source=app_share&type=normal&xsec_token=CBUD1EVtTBvYvwum6k6I8QLd6l_uIs6tIanyR4l6dTmd4=&author_share=1&xhsshare=CopyLink&shareRedId=ODZFODc1Rzk2NzUyOTgwNjY0OTc1SD5P&apptime=1778708999&share_id=a512da2b2c7d4303b83d32d6095d0734

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
**final** S&P basket excludes the sister's current top picks:

1. Read the sister's current top-3 open picks. The backtest prefers the sister's
   live dashboard (`http://127.0.0.1:8765/api/picks`, override with
   `NASDAQ_PICKS_URL`) because that is recomputed each request and stays fresher
   than its on-disk CSV; if the dashboard is offline it falls back to
   `.../nasdaq100_momentum_backtest/outputs/open_rebalance_picks.csv`
   (override with `NASDAQ_OPEN_PATH`).
2. Drop any of those sister tickers from the S&P 500 Titan-12 ranking.
3. Backfill from the next-highest S&P 500 Titan-12 ranked names until 3 names
   are selected.

The result is written to `outputs/final_rebalance_picks.csv` and reported as
`Final Top 3 (Nasdaq-Overlap Excluded)` in `summary.md`, alongside the
pre-exclusion `Baseline Open Basket`. This final basket is the intended
tradeable set; the dashboard's headline "Current Basket" shows it too.

## Local Dashboard

Start the local dashboard from the project virtual environment:

```bash
.venv/bin/python run_webapp.py
```

Then open:

```text
http://127.0.0.1:8766/
```

By default the dashboard binds to `127.0.0.1` on port `8766`. Override the host
or port with environment variables:

```bash
TITAN12_HOST=0.0.0.0 TITAN12_PORT=8767 .venv/bin/python run_webapp.py
```

The dashboard reads the local `outputs/` CSVs and charts. It shows headline
stats, the Nasdaq-overlap-excluded current basket, the last 12
Nasdaq-overlap-excluded rebalance baskets, and the recent-rebalances chart.

## Cloudflare Pages Static Deployment

The local dashboard can be exported as static files for Cloudflare Pages:

```bash
.venv/bin/python scripts/export_static_dashboard.py --output-dir public
```

The static export writes:

```text
public/index.html
public/app.js
public/dashboard.json
public/charts/*.png
```

For automated monthly updates, this repo includes:

```text
.github/workflows/cloudflare-pages-dashboard.yml
```

The workflow runs after the US market close on weekdays, checks whether the
date is the first NYSE-style trading day of the month, then:

1. Builds the approximate Wikipedia historical S&P 500 membership file.
2. Checks out `cozec/momentum_6month_claude` and runs the Nasdaq source
   backtest to generate overlap exclusions.
3. Runs the S&P 500 historical-membership backtest through the current date.
4. Exports the dashboard to `public/`.
5. Deploys `public/` to Cloudflare Pages with Wrangler direct upload.

Add these GitHub repository secrets before enabling the workflow:

```text
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_API_TOKEN
CLOUDFLARE_PAGES_PROJECT_NAME
```

The Cloudflare API token needs `Account > Cloudflare Pages > Edit` permission.
If the Nasdaq repo is private, also add `NASDAQ_REPO_TOKEN` with read access to
`cozec/momentum_6month_claude`; public repos do not need this extra token.
You can also run the workflow manually from GitHub Actions with
`force_update=true`.

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

### Wikipedia History Bootstrap

For a good-enough research bootstrap, build an approximate point-in-time file
from Wikipedia's current S&P 500 table plus its selected add/remove history:

```bash
.venv/bin/python scripts/build_wikipedia_sp500_membership.py
```

This writes:

```text
data/sp500_membership_wikipedia_history.csv
```

Review the generated file before promoting it:

```bash
cp data/sp500_membership.csv data/sp500_membership.current_constituents.csv
cp data/sp500_membership_wikipedia_history.csv data/sp500_membership.csv
.venv/bin/python main.py --membership-mode historical_constituents --refresh-data
```

This Wikipedia-derived file is still approximate. It is better than using only
today's constituents, but it can have unknown start dates, missing sectors for
removed companies, ticker-history gaps, and omissions from Wikipedia's selected
changes table. For production-grade research, use a paid point-in-time index
constituent source such as CRSP, Compustat/Capital IQ, Bloomberg, Refinitiv,
Norgate, or another licensed dataset.

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
