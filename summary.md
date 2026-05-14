# Titan-12 Momentum Rotation Summary

Run timestamp: 2026-05-14T02:07:15.777474+00:00

Data freshness timestamp: 2026-05-01


> WARNING: This run used current S&P 500 constituents and is survivorship-biased.

## Run configuration

| Parameter | Value |
|-----------|-------|
| Strategy | Titan-12 Momentum Rotation: top-3 equal-weight, 12-step weighted monthly momentum |
| Universe | Current S&P 500 from Wikipedia (503 rows, including share classes; survivorship-biased) |
| Data window | 2016-01-01 -> 2026-05-12 |
| Realized backtest window | 2017-02-01 entry -> 2026-05-01 exit |
| Lookback | 12 completed months |
| Score method | `sum(weight_i * monthly_return_i)`, weights 1..12 from oldest to newest |
| Rebalance frequency | First trading day of each month |
| Transaction cost | 5 bps |
| Slippage | 5 bps |
| Initial capital | $100,000 |
| Primary benchmark | SPY |
| Rebalances executed | 111 |
| Tickers with downloaded price history | 503 of 503 current constituents, plus SPY |

## Headline results

| Metric | Strategy | SPY B&H |
|--------|---------:|--------:|
| CAGR | **33.16%** | 15.08% |
| Annualized volatility | 40.03% | 16.60% |
| Sharpe ratio | 0.91 | **0.94** |
| Max drawdown | -36.67% | **-23.79%** |
| Total return | **+1,314%** | +267% |
| Final value (from $100k) | **$1,413,882** | $366,701 |
| Average monthly return | **3.05%** | 1.29% |
| Median monthly return | **2.44%** | 2.05% |
| Best month | **+41.45%** | +14.89% |
| Worst month | -26.68% | **-19.89%** |
| Win rate vs SPY (months) | 50.5% | — |
| Average turnover | 42.34%/mo | — |

## Active Configuration

| setting              | value                |
|:---------------------|:---------------------|
| start_date           | 2016-01-01           |
| end_date             | 2026-05-12           |
| top_n                | 3                    |
| benchmark            | SPY                  |
| transaction_cost_bps | 5.0                  |
| slippage_bps         | 5.0                  |
| membership_mode      | current_constituents |

## Summary Stats

|   total_return |     CAGR |   annualized_volatility |   Sharpe_ratio |   Sortino_ratio |   max_drawdown |   Calmar_ratio |   monthly_win_rate |   win_rate_vs_SPY |   average_monthly_return |   median_monthly_return |   best_month |   worst_month |   number_of_rebalances |   average_turnover | average_holding_period   |
|---------------:|---------:|------------------------:|---------------:|----------------:|---------------:|---------------:|-------------------:|------------------:|-------------------------:|------------------------:|-------------:|--------------:|-----------------------:|-------------------:|:-------------------------|
|        13.1388 | 0.331585 |                0.400283 |       0.913994 |         1.79014 |      -0.366696 |       0.904251 |           0.567568 |          0.504505 |                 0.030488 |               0.0243899 |     0.414487 |     -0.266813 |                    111 |           0.423423 | 1 month                  |

## Latest Completed Rebalance

2026-04-01: SNDK, LITE, CIEN

## Current Open Basket

May 2026 open basket as of 2026-05-12: SNDK, LITE, INTC

## Top 3 Selections Over Past 1 Year

Latest 12 completed monthly rebalances:

| Rebalance | Rank 1 | Rank 2 | Rank 3 |
|-----------|--------|--------|--------|
| 2025-05-01 | PLTR | AXON | GEV |
| 2025-06-02 | PLTR | GEV | NRG |
| 2025-07-01 | PLTR | COIN | GEV |
| 2025-08-01 | PLTR | GEV | COIN |
| 2025-09-02 | PLTR | GEV | STX |
| 2025-10-01 | HOOD | APP | WDC |
| 2025-11-03 | WDC | HOOD | MU |
| 2025-12-01 | WDC | MU | STX |
| 2026-01-02 | WDC | MU | WBD |
| 2026-02-02 | MU | WDC | STX |
| 2026-03-02 | SNDK | WDC | CIEN |
| 2026-04-01 | SNDK | LITE | CIEN |

## Nasdaq-Overlap-Excluded Top 3

Rule: for each S&P 500 rebalance date, first read the sister Nasdaq strategy's
top-3 selections from
`/Users/adam/project/momentum_6m/nasdaq100_momentum_backtest/outputs/monthly_selections.csv`.
If any of those tickers appear in the S&P 500 Titan-12 ranking for the same
rebalance date, skip them and backfill from the next-highest S&P 500 Titan-12
ranked stocks.

Latest 12 completed monthly rebalances after applying the Nasdaq exclusion:

| Rebalance | Nasdaq excluded | Adjusted Rank 1 | Adjusted Rank 2 | Adjusted Rank 3 |
|-----------|-----------------|-----------------|-----------------|-----------------|
| 2025-05-01 | PLTR, APP, MSTR | AXON | GEV | NFLX |
| 2025-06-02 | PLTR, AVGO, CRWD | GEV | NRG | AXON |
| 2025-07-01 | PLTR, STX, ZS | COIN | GEV | AXON |
| 2025-08-01 | PLTR, STX, WDC | GEV | COIN | TPR |
| 2025-09-02 | PLTR, ALNY, INSM | GEV | STX | WDC |
| 2025-10-01 | SNDK, WDC, APP | HOOD | STX | WBD |
| 2025-11-03 | SNDK, WDC, MU | HOOD | STX | WBD |
| 2025-12-01 | SNDK, WDC, INSM | MU | STX | WBD |
| 2026-01-02 | SNDK, WDC, WBD | MU | STX | ALB |
| 2026-02-02 | SNDK, MU, WDC | STX | LRCX | ALB |
| 2026-03-02 | SNDK, WDC, MU | CIEN | TER | STX |
| 2026-04-01 | SNDK, WDC, MU | LITE | CIEN | SATS |

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
- outputs/charts/recent_rebalances.png


## Test Results

`.venv/bin/pytest` completed successfully after the run.

Result: 9 passed, 15 third-party dependency warnings.
