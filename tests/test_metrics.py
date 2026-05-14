"""Tests for performance metric generation."""

from __future__ import annotations

import pandas as pd

from src.metrics import calculate_summary_stats


def test_summary_stats_basic_shape() -> None:
    """Summary stats should include required headline metrics."""

    returns = [0.01, -0.02, 0.03]
    values = [101000.0, 98980.0, 101949.4]
    portfolio_returns = pd.DataFrame(
        {
            "portfolio_return_net": returns,
            "spy_return": [0.0, 0.0, 0.0],
            "portfolio_value": values,
            "turnover": [1.0, 0.5, 0.5],
        }
    )
    stats = calculate_summary_stats(portfolio_returns)
    assert not stats.empty
    assert "Sharpe_ratio" in stats.columns
    assert stats.loc[0, "number_of_rebalances"] == 3
