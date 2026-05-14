"""Performance metrics for monthly backtest returns."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _max_drawdown(values: pd.Series) -> float:
    """Calculate maximum drawdown from an equity curve."""

    if values.empty:
        return np.nan
    running_max = values.cummax()
    drawdown = values / running_max - 1.0
    return float(drawdown.min())


def calculate_summary_stats(portfolio_returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate common monthly strategy performance statistics."""

    if portfolio_returns.empty:
        return pd.DataFrame()

    returns = pd.to_numeric(
        portfolio_returns["portfolio_return_net"], errors="coerce"
    ).dropna()
    spy_returns = pd.to_numeric(portfolio_returns.get("spy_return"), errors="coerce")
    values = pd.to_numeric(portfolio_returns["portfolio_value"], errors="coerce").dropna()
    if returns.empty or values.empty:
        return pd.DataFrame()

    periods = len(returns)
    years = periods / 12.0
    total_return = float(values.iloc[-1] / values.iloc[0] / (1 + returns.iloc[0]) - 1.0)
    if "portfolio_value" in portfolio_returns:
        initial_equity = values.iloc[0] / (1 + returns.iloc[0])
        total_return = float(values.iloc[-1] / initial_equity - 1.0)
    cagr = float((1.0 + total_return) ** (1.0 / years) - 1.0) if years > 0 else np.nan
    annualized_volatility = float(returns.std(ddof=1) * np.sqrt(12)) if periods > 1 else np.nan
    sharpe_ratio = (
        float(returns.mean() / returns.std(ddof=1) * np.sqrt(12))
        if periods > 1 and returns.std(ddof=1) != 0
        else np.nan
    )
    downside = returns[returns < 0]
    sortino_ratio = (
        float(returns.mean() / downside.std(ddof=1) * np.sqrt(12))
        if len(downside) > 1 and downside.std(ddof=1) != 0
        else np.nan
    )
    max_drawdown = _max_drawdown(values)
    calmar_ratio = float(cagr / abs(max_drawdown)) if max_drawdown < 0 else np.nan
    monthly_win_rate = float((returns > 0).mean())
    win_rate_vs_spy = (
        float((returns.reset_index(drop=True) > spy_returns.reset_index(drop=True)).mean())
        if spy_returns.notna().any()
        else np.nan
    )
    average_turnover = float(portfolio_returns["turnover"].mean())

    stats = {
        "total_return": total_return,
        "CAGR": cagr,
        "annualized_volatility": annualized_volatility,
        "Sharpe_ratio": sharpe_ratio,
        "Sortino_ratio": sortino_ratio,
        "max_drawdown": max_drawdown,
        "Calmar_ratio": calmar_ratio,
        "monthly_win_rate": monthly_win_rate,
        "win_rate_vs_SPY": win_rate_vs_spy,
        "average_monthly_return": float(returns.mean()),
        "median_monthly_return": float(returns.median()),
        "best_month": float(returns.max()),
        "worst_month": float(returns.min()),
        "number_of_rebalances": int(periods),
        "average_turnover": average_turnover,
        "average_holding_period": "1 month",
    }
    return pd.DataFrame([stats])
