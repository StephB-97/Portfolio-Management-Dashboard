# You can reduce risk without reducing return by combining assets that dont move together.
#Sharpe Ratio : (Portfolio Return - Risk Free Rate) / Portfolio Volatility
# return = how much money you make on an investment 
# Risk free rate = what you would get from a risk free investment (US treaury - 5%)
# volatility = how wildly the portfolio swings
# Higher Sharpe means more return per unit of risk taken 
# The goal is to find what percentage should go in each stock that maximizes the weight.

import numpy as np
import pandas as pd
from scipy.optimize import minimize

RISK_FREE_RATE = 0.05
TRADING_DAYS   = 252

def compute_portfolio_metrics(weights, mean_returns, cov_matrix):
    """
    Given weights, calculates return, volatility, and Sharpe ratio.
    
    THE MATH:
    - Return     = weights · mean_returns  (dot product)
    - Variance   = weights^T × cov_matrix × weights  (matrix multiplication)
    - Volatility = sqrt(variance)
    - Sharpe     = (Return - Risk Free Rate) / Volatility
    """
    port_return = float(np.dot(weights, mean_returns))
    port_vol    = float(np.sqrt(weights @ cov_matrix.values @ weights))
    sharpe      = (port_return - RISK_FREE_RATE) / port_vol if port_vol > 0 else 0.0
    return {
        "return":     port_return,
        "volatility": port_vol,
        "sharpe":     sharpe,
    }


def maximize_sharpe(returns_df):
    """
    Finds the weights that maximize the Sharpe ratio.
    
    HOW scipy WORKS:
    It tries thousands of weight combinations, evaluates Sharpe
    each time, and converges on the best one.
    We pass NEGATIVE Sharpe because scipy can only minimize —
    minimizing -Sharpe is the same as maximizing Sharpe.
    
    Constraints:
    - Weights must sum to 1.0  (invest 100% of capital)
    - Each weight between 0 and 1  (no short selling)
    """
    n            = len(returns_df.columns)
    tickers      = list(returns_df.columns)
    mean_returns = returns_df.mean() * TRADING_DAYS
    cov_matrix   = returns_df.cov()  * TRADING_DAYS
    equal_w      = np.array([1 / n] * n)

    def negative_sharpe(w):
        m = compute_portfolio_metrics(w, mean_returns, cov_matrix)
        return -m["sharpe"]

    result = minimize(
        negative_sharpe,
        equal_w,
        method="SLSQP",
        bounds=tuple((0, 1) for _ in range(n)),
        constraints={"type": "eq", "fun": lambda w: np.sum(w) - 1},
    )

    opt_weights = result.x if result.success else equal_w

    return {
        "weights":       opt_weights,
        "tickers":       tickers,
        "metrics":       compute_portfolio_metrics(opt_weights, mean_returns, cov_matrix),
        "equal_metrics": compute_portfolio_metrics(equal_w,    mean_returns, cov_matrix),
        "success":       result.success,
    }