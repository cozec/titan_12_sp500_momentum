"""Tests for portfolio execution helpers."""

from __future__ import annotations

import pandas as pd

from src.backtest import calculate_portfolio_return, calculate_turnover


def test_portfolio_return_equal_weight() -> None:
    """Portfolio return should be the average selected stock return."""

    prices = pd.DataFrame(
        {
            "AAA": [100.0, 110.0],
            "BBB": [50.0, 45.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-02-01"]),
    )
    portfolio_return, details = calculate_portfolio_return(
        ["AAA", "BBB"], prices, "2024-01-02", "2024-02-01"
    )
    assert round(portfolio_return, 10) == round(((0.10 + -0.10) / 2), 10)
    assert len(details) == 2


def test_turnover_from_one_equal_weight_basket_to_another() -> None:
    """One replacement in a three-stock equal-weight basket is 1/3 turnover."""

    turnover = calculate_turnover({"AAA", "BBB", "CCC"}, {"AAA", "BBB", "DDD"})
    assert round(turnover, 10) == round(1 / 3, 10)


def test_turnover_first_portfolio_is_full_turnover() -> None:
    """Opening a new portfolio should count as full turnover."""

    assert calculate_turnover(set(), {"AAA", "BBB", "CCC"}) == 1.0
