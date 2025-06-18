# performance_metrics.py
import numpy as np

def sharpe_ratio(pnl_series):
    returns = np.diff(pnl_series)
    if np.std(returns) == 0:
        return 0
    return np.mean(returns) / np.std(returns) * np.sqrt(252)

def sortino_ratio(pnl_series):
    returns = np.diff(pnl_series)
    downside = returns[returns < 0]
    if len(downside) == 0:
        return np.inf
    downside_std = np.std(downside)
    return np.mean(returns) / downside_std * np.sqrt(252)

def max_drawdown(pnl_series):
    pnl_array = np.array(pnl_series)
    peak = np.maximum.accumulate(pnl_array)
    drawdown = peak - pnl_array
    return np.max(drawdown)

def realized_unrealized_pnl(cash, inventory, current_price, avg_entry_price=None):
    realized = cash
    unrealized = inventory * current_price
    return realized, unrealized
