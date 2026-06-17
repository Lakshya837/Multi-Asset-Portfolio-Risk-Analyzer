"""
Multi-Asset Portfolio Risk Analyzer

Features:
- Risk Metrics (Sharpe, Sortino, VaR, Max Drawdown)
- Correlation Analysis
- Portfolio Optimization
- Monte Carlo Simulation
- Efficient Frontier
- Portfolio Backtesting
- Portfolio Allocation Visualization

Author: Lakshya Kumar
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)


# ==================================================
# 1. PROJECT SETTINGS
# ==================================================

TRADING_DAYS   = 252
RISK_FREE_RATE = 0.06
NUM_PORTFOLIOS = 5000

# Diversified portfolio of 15 NSE stocks
STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "SUNPHARMA.NS",
    "DRREDDY.NS",
    "ASIANPAINT.NS",
    "MARUTI.NS",
    "BHARTIARTL.NS",
    "ONGC.NS",
    "WIPRO.NS",
]


# ==================================================
# 2. RISK METRIC FUNCTIONS
# ==================================================

def calculate_annual_return(returns):
    """
    Annualised Return

    Formula:
    Mean Daily Return × 252
    """
    return returns.mean() * TRADING_DAYS


def calculate_annual_volatility(returns):
    """
    Annualised Volatility

    Formula:
    Daily Standard Deviation × sqrt(252)

    Measures risk.
    """
    return returns.std() * np.sqrt(TRADING_DAYS)


def calculate_sharpe_ratio(
    annual_return,
    annual_volatility,
    risk_free_rate
):
    """
    Sharpe Ratio

    Formula:
    (Return - Risk Free Rate) / Volatility
    """
    return (
        annual_return - risk_free_rate
    ) / annual_volatility


def calculate_sortino_ratio(
    returns,
    annual_return,
    risk_free_rate
):
    """
    Sortino Ratio

    Similar to Sharpe Ratio,
    but only penalises downside volatility.
    """

    downside_returns = returns.copy()

    # Keep only negative returns
    downside_returns[downside_returns > 0] = 0

    downside_volatility = (
        downside_returns.std()
        * np.sqrt(TRADING_DAYS)
    )

    sortino_ratio = (
        annual_return - risk_free_rate
    ) / downside_volatility

    return sortino_ratio


def calculate_var_95(returns):
    """
    Historical Value at Risk (95%)

    Interpretation:
    95% of days performed better than this value.
    """
    return np.percentile(returns, 5)


def calculate_max_drawdown(returns):
    """
    Maximum Drawdown

    Measures the largest percentage decline
    from a previous peak.
    """

    # Convert returns into cumulative growth
    cumulative_returns = (1 + returns).cumprod()

    # Running highest value reached so far
    running_max = cumulative_returns.cummax()

    # Calculate drawdowns
    drawdown = (
        cumulative_returns - running_max
    ) / running_max

    # Worst drawdown
    max_drawdown = drawdown.min()

    return max_drawdown


# ==================================================
# 3. PORTFOLIO FUNCTIONS
# ==================================================

def calculate_portfolio_return(
    weights,
    annual_returns
):
    """
    Portfolio Return

    Weighted average return
    of all assets.
    """
    return np.sum(
        weights * annual_returns
    )


def calculate_portfolio_volatility(
    weights,
    returns
):
    """
    Portfolio Volatility

    Uses covariance matrix and
    Modern Portfolio Theory.
    """

    covariance_matrix = (
        returns.cov()
        * TRADING_DAYS
    )

    portfolio_variance = np.dot(
        weights.T,
        np.dot(
            covariance_matrix,
            weights
        )
    )

    portfolio_volatility = np.sqrt(
        portfolio_variance
    )

    return portfolio_volatility


def generate_random_portfolios(
    num_portfolios,
    annual_returns,
    returns
):
    """
    Generate random portfolios.

    Returns:
    - portfolio returns
    - portfolio volatility
    - portfolio sharpe ratio
    - portfolio weights
    """

    results = []

    all_weights = []

    num_assets = len(annual_returns)

    for _ in range(num_portfolios):

        # Generate random weights
        weights = np.random.random(
            num_assets
        )

        # Make weights sum to 1
        weights = (
            weights / np.sum(weights)
        )

        portfolio_return = (
            calculate_portfolio_return(
                weights,
                annual_returns
            )
        )

        portfolio_volatility = (
            calculate_portfolio_volatility(
                weights,
                returns
            )
        )

        portfolio_sharpe = (
            portfolio_return
            - RISK_FREE_RATE
        ) / portfolio_volatility

        results.append([
            portfolio_return,
            portfolio_volatility,
            portfolio_sharpe
        ])

        all_weights.append(weights)

    return (
        np.array(results),
        np.array(all_weights)
    )


# ==================================================
# 4. DOWNLOAD DATA
# ==================================================

print("\nDownloading stock data...")

data = yf.download(
    STOCKS,
    period="3y",
    auto_adjust=True
)

# Extract closing prices
prices = data["Close"]


# ==================================================
# 5. DATA CHECKS
# ==================================================

print("\nMissing Values:")
print(prices.isnull().sum())

print("\nPrice Data Shape:")
print(prices.shape)


# ==================================================
# 6. RETURN CALCULATIONS
# ==================================================

returns = prices.pct_change().dropna()

print("\nReturns Shape:")
print(returns.shape)

print("\nFirst 5 Return Rows:")
print(returns.head())


# ==================================================
# 7. STOCK RISK METRICS
# ==================================================

# Annualised returns and volatility
annual_returns = calculate_annual_return(returns)

annual_volatility = calculate_annual_volatility(returns)

# Sharpe Ratio
sharpe_ratio = calculate_sharpe_ratio(
    annual_returns,
    annual_volatility,
    RISK_FREE_RATE
)

# Sortino Ratio
sortino_ratio = calculate_sortino_ratio(
    returns,
    annual_returns,
    RISK_FREE_RATE
)

# Value at Risk (95%)
var_95 = returns.apply(calculate_var_95)

# Maximum Drawdown
max_drawdown = returns.apply(
    calculate_max_drawdown
)


# ==================================================
# 8. CORRELATION ANALYSIS
# ==================================================
# Correlation tells us how similarly two stocks move.
#
# +1 = move together perfectly
#  0 = no relationship
# -1 = move opposite each other
#
# Correlation is the foundation of diversification.

correlation_matrix = returns.corr()

print("\nCorrelation Matrix:")
print(correlation_matrix)


# ==================================================
# 9. EQUAL WEIGHT PORTFOLIO
# ==================================================

num_assets = len(STOCKS)

equal_weights = np.array(
    [1 / num_assets] * num_assets
)

print("\nEqual Portfolio Weights:")
print(equal_weights)

portfolio_return = calculate_portfolio_return(
    equal_weights,
    annual_returns
)

portfolio_volatility = (
    calculate_portfolio_volatility(
        equal_weights,
        returns
    )
)

portfolio_sharpe = (
    portfolio_return
    - RISK_FREE_RATE
) / portfolio_volatility

print("\nEqual Weight Portfolio Metrics")

print(
    f"Annual Return: "
    f"{portfolio_return * 100:.2f}%"
)

print(
    f"Annual Volatility: "
    f"{portfolio_volatility * 100:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{portfolio_sharpe:.2f}"
)


# ==================================================
# 10. MONTE CARLO SIMULATION
# ==================================================

portfolio_results, portfolio_weights = (
    generate_random_portfolios(
        NUM_PORTFOLIOS,
        annual_returns,
        returns
    )
)

print(
    f"\nGenerated "
    f"{NUM_PORTFOLIOS} portfolios."
)


# ==================================================
# 11. OPTIMAL PORTFOLIO SELECTION
# ==================================================

# Maximum Sharpe Portfolio
max_sharpe_index = np.argmax(
    portfolio_results[:, 2]
)

max_sharpe_portfolio = (
    portfolio_results[
        max_sharpe_index
    ]
)

max_sharpe_weights = (
    portfolio_weights[
        max_sharpe_index
    ]
)

# Minimum Variance Portfolio
min_volatility_index = np.argmin(
    portfolio_results[:, 1]
)

min_volatility_portfolio = (
    portfolio_results[
        min_volatility_index
    ]
)

min_variance_weights = (
    portfolio_weights[
        min_volatility_index
    ]
)

print("\nMaximum Sharpe Portfolio Weights")

for stock, weight in zip(
    STOCKS,
    max_sharpe_weights
):
    print(
        f"{stock}: "
        f"{weight * 100:.2f}%"
    )

print("\nMinimum Variance Portfolio Weights")

for stock, weight in zip(
    STOCKS,
    min_variance_weights
):
    print(
        f"{stock}: "
        f"{weight * 100:.2f}%"
    )

print("\nMaximum Sharpe Portfolio")

print(
    f"Return: "
    f"{max_sharpe_portfolio[0] * 100:.2f}%"
)

print(
    f"Volatility: "
    f"{max_sharpe_portfolio[1] * 100:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{max_sharpe_portfolio[2]:.2f}"
)

print("\nMinimum Variance Portfolio")

print(
    f"Return: "
    f"{min_volatility_portfolio[0] * 100:.2f}%"
)

print(
    f"Volatility: "
    f"{min_volatility_portfolio[1] * 100:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{min_volatility_portfolio[2]:.2f}"
)


# ==================================================
# 12. BACKTESTING
# ==================================================

# --- Daily Portfolio Returns ---
# Calculate daily returns for:
# 1. Equal Weight Portfolio
# 2. Minimum Variance Portfolio
# 3. Maximum Sharpe Portfolio

equal_portfolio_returns = (
    returns @ equal_weights
)

min_variance_returns = (
    returns @ min_variance_weights
)

max_sharpe_returns = (
    returns @ max_sharpe_weights
)

# --- Cumulative Growth ---
# Simulate growth of ₹1 invested

equal_growth = (
    1 + equal_portfolio_returns
).cumprod()

min_variance_growth = (
    1 + min_variance_returns
).cumprod()

max_sharpe_growth = (
    1 + max_sharpe_returns
).cumprod()

# --- Performance Summary ---

print("\nPortfolio Backtest Results")

print(
    f"Equal Weight Final Value: "
    f"{equal_growth.iloc[-1]:.2f}"
)

print(
    f"Minimum Variance Final Value: "
    f"{min_variance_growth.iloc[-1]:.2f}"
)

print(
    f"Maximum Sharpe Final Value: "
    f"{max_sharpe_growth.iloc[-1]:.2f}"
)

print()

print(
    f"Equal Weight Total Return: "
    f"{(equal_growth.iloc[-1]-1)*100:.2f}%"
)

print(
    f"Minimum Variance Total Return: "
    f"{(min_variance_growth.iloc[-1]-1)*100:.2f}%"
)

print(
    f"Maximum Sharpe Total Return: "
    f"{(max_sharpe_growth.iloc[-1]-1)*100:.2f}%"
)


# ==================================================
# 13. RISK METRICS SUMMARY TABLE
# ==================================================

summary_df = pd.DataFrame({
    "Annual Return":     annual_returns,
    "Annual Volatility": annual_volatility,
    "Sharpe Ratio":      sharpe_ratio,
    "Sortino Ratio":     sortino_ratio,
    "VaR 95%":           var_95,
    "Max Drawdown":      max_drawdown,
})

display_df = summary_df.copy()

# Convert decimals to percentages
display_df["Annual Return"]     *= 100
display_df["Annual Volatility"] *= 100
display_df["VaR 95%"]           *= 100
display_df["Max Drawdown"]      *= 100

# Round values
display_df = display_df.round(2)

# Sort by best Sortino Ratio
display_df = display_df.sort_values(
    by="Sortino Ratio",
    ascending=False
)

print("\nRisk Metrics Summary:")
print(display_df)


# ==================================================
# 14. VISUALIZATIONS
# ==================================================

# --- Correlation Heatmap ---
# Visual representation of the correlation matrix.
# Darker colors indicate stronger relationships.

plt.figure(figsize=(14, 10))

sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)

plt.title(
    "Correlation Heatmap of NSE Stocks"
)

plt.tight_layout()

plt.show()

# --- Efficient Frontier ---

plt.figure(figsize=(14, 10))

scatter = plt.scatter(
    portfolio_results[:, 1] * 100,
    portfolio_results[:, 0] * 100,
    c=portfolio_results[:, 2],
    cmap="viridis",
    alpha=0.6
)

plt.colorbar(
    scatter,
    label="Sharpe Ratio"
)

# Maximum Sharpe Portfolio
plt.scatter(
    max_sharpe_portfolio[1] * 100,
    max_sharpe_portfolio[0] * 100,
    color="red",
    s=300,
    marker="*",
    label="Maximum Sharpe"
)

# Minimum Variance Portfolio
plt.scatter(
    min_volatility_portfolio[1] * 100,
    min_volatility_portfolio[0] * 100,
    color="blue",
    s=300,
    marker="*",
    label="Minimum Variance"
)

plt.xlabel("Annual Volatility (%)")
plt.ylabel("Annual Return (%)")

plt.title(
    "Efficient Frontier - NSE Portfolio Universe"
)

plt.legend()

plt.grid(True)

plt.show()

# --- Maximum Sharpe Allocation Pie ---

plt.figure(figsize=(10, 8))

plt.pie(
    max_sharpe_weights,
    labels=STOCKS,
    autopct="%1.1f%%"
)

plt.title(
    "Maximum Sharpe Portfolio Allocation"
)

plt.show()

# --- Minimum Variance Allocation Pie ---

plt.figure(figsize=(10, 8))

plt.pie(
    min_variance_weights,
    labels=STOCKS,
    autopct="%1.1f%%"
)

plt.title(
    "Minimum Variance Portfolio Allocation"
)

plt.show()

# --- Backtest Performance Chart ---

plt.figure(figsize=(14, 8))

plt.plot(
    equal_growth,
    label="Equal Weight Portfolio"
)

plt.plot(
    min_variance_growth,
    label="Minimum Variance Portfolio"
)

plt.plot(
    max_sharpe_growth,
    label="Maximum Sharpe Portfolio"
)

plt.title(
    "Portfolio Backtest Performance"
)

plt.xlabel("Date")

plt.ylabel(
    "Portfolio Value (Starting = ₹1)"
)

plt.legend()

plt.grid(True)

plt.show()

print("\nAnalysis Complete.")