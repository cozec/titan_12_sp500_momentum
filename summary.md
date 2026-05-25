# Titan-12 Momentum Rotation Summary

Run timestamp: 2026-05-25T22:46:01.130128+00:00

Data freshness timestamp: 2026-05-01


## Active Configuration

| setting              | value                   |
|:---------------------|:------------------------|
| start_date           | 2016-01-01              |
| end_date             | 2026-05-12              |
| top_n                | 3                       |
| benchmark            | SPY                     |
| transaction_cost_bps | 5.0                     |
| slippage_bps         | 5.0                     |
| membership_mode      | historical_constituents |

## Summary Stats

|   total_return |     CAGR |   annualized_volatility |   Sharpe_ratio |   Sortino_ratio |   max_drawdown |   Calmar_ratio |   monthly_win_rate |   win_rate_vs_SPY |   average_monthly_return |   median_monthly_return |   best_month |   worst_month |   number_of_rebalances |   average_turnover | average_holding_period   |
|---------------:|---------:|------------------------:|---------------:|----------------:|---------------:|---------------:|-------------------:|------------------:|-------------------------:|------------------------:|-------------:|--------------:|-----------------------:|-------------------:|:-------------------------|
|        8.71366 | 0.278628 |                0.400046 |       0.811646 |         1.56194 |      -0.393273 |       0.708485 |           0.558559 |          0.459459 |                0.0270579 |               0.0235812 |     0.414487 |     -0.304786 |                    111 |           0.435435 | 1 month                  |

## Backtest Results Details

This run used the Wikipedia-derived historical membership bootstrap in
`data/sp500_membership.csv`, replacing the previous current-constituents-only
file. The previous file was backed up as
`data/sp500_membership.current_constituents.20260525.csv`.

| metric | value |
|:--|--:|
| Initial capital | $100,000 |
| Final strategy value | $971,366 |
| Final SPY value | $366,701 |
| Strategy total return | 871.37% |
| Strategy CAGR | 27.86% |
| SPY total return over matched run | 266.70% |
| Annualized volatility | 40.00% |
| Sharpe ratio | 0.81 |
| Sortino ratio | 1.56 |
| Max drawdown | -39.33% |
| Monthly win rate | 55.86% |
| Win rate vs SPY | 45.95% |
| Average monthly turnover | 43.54% |
| Completed rebalance periods | 111 |

The latest completed holding period was the April 1, 2026 rebalance through
May 1, 2026. The strategy returned 41.45% net versus 9.98% for SPY during that
period.

| ticker | company | rank | entry | exit | return |
|:--|:--|--:|--:|--:|--:|
| SNDK | Sandisk | 1 | $692.73 | $1,187.00 | 71.35% |
| LITE | Lumentum | 2 | $764.65 | $949.93 | 24.23% |
| CIEN | Ciena | 3 | $415.39 | $535.29 | 28.86% |

Important caveat: this is an improvement over survivorship-biased
current-constituents testing, but it is not institutional point-in-time data.
The Wikipedia history has unknown start dates for some removed members, missing
sector classifications for many historical names, and ticker-history gaps.
Yahoo Finance also does not provide usable price data for many delisted or
acquired tickers.

## Latest Completed Rebalance

2026-04-01: SNDK, LITE, CIEN

## Current Open Basket

SNDK, LITE, CIEN

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

Full details are in `logs/data_quality_report.csv`.

| issue_type | count |
|:--|--:|
| insufficient_history | 6,040 |
| missing_price_history | 4,287 |
| download_failed | 174 |
| insufficient_selection_count | 13 |

Representative failed Yahoo downloads include ABK, ABMD, ACAS, ACE, ADS, AGN,
AKS, ALTR, ALXN, ANR, ANSS, APOL, ARG, ARNC, ATVI, AVP, AYE, BCR, BHI, BIG,
BJS, BRCM, BS, BXLT, CELG, CEPH, CERN, CFN, CHK, and CMA.

## Test Results

Not run by backtest command.
