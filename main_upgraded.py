"""Multi-Asset Portfolio Risk Analyzer — rolling out-of-sample edition.

Preserves the original project's 15-stock universe, Monte Carlo portfolio
sampling, Equal-Weight / Maximum-Sharpe / Minimum-Variance strategies, and
risk analytics while adding rolling out-of-sample testing and a Nifty 50
price-index benchmark.

Important assumptions:
- Yahoo Finance adjusted prices are used for equities (auto_adjust=True).
- ^NSEI is a PRICE index, not the Nifty 50 Total Return Index (TRI); its
  benchmark returns therefore generally exclude dividends.
- Long-only weights: each weight >= 0 and weights sum to 1; no leverage.
- 252 trading days/year; 252 daily observations for each training window.
- Re-estimate monthly (every 21 trading observations) and hold weights fixed
  during the following test window.
- Transaction costs are a configurable sensitivity assumption, not a broker quote.
- This is historical research, not investment advice or a return forecast.
"""

from pathlib import Path
import warnings

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# 1. PROJECT SETTINGS
# ============================================================

SEED = 42
TRADING_DAYS = 252
RISK_FREE_RATE = 0.06
NUM_PORTFOLIOS = 5_000
TRAINING_DAYS = 252
TEST_DAYS = 21                 # approximately one trading month
TRANSACTION_COST_BPS = 10      # sensitivity assumption: 10 bps per 1.0 turnover
DOWNLOAD_PERIOD = "5y"         # longer history enables more rolling test windows
OUTPUT_DIR = Path("outputs")

np.random.seed(SEED)
OUTPUT_DIR.mkdir(exist_ok=True)

STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "SUNPHARMA.NS", "DRREDDY.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "BHARTIARTL.NS", "ONGC.NS", "WIPRO.NS",
]
BENCHMARK = "^NSEI"  # Nifty 50 price index, not TRI

# ============================================================
# 2. DOWNLOAD AND VALIDATE DATA
# ============================================================

def download_prices():
    """Download adjusted equity prices and the Nifty 50 index series."""
    tickers = STOCKS + [BENCHMARK]
    print(f"Downloading {len(tickers)} series over {DOWNLOAD_PERIOD}...")

    raw = yf.download(
        tickers,
        period=DOWNLOAD_PERIOD,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no data. Check internet access/tickers and retry.")

    if isinstance(raw.columns, pd.MultiIndex):
        field = "Close" if "Close" in raw.columns.get_level_values(0) else None
        if field is None:
            raise RuntimeError("Could not find the Close price field in downloaded data.")
        prices = raw[field].copy()
    else:
        # Defensive fallback in case the provider returns a flat column index.
        if "Close" not in raw.columns:
            raise RuntimeError("Could not find Close prices in downloaded data.")
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    prices = prices.sort_index()

    missing_tickers = [ticker for ticker in tickers if ticker not in prices.columns]
    if missing_tickers:
        raise RuntimeError(f"Missing ticker columns from download: {missing_tickers}")

    prices = prices[tickers].apply(pd.to_numeric, errors="coerce")
    missing_report = pd.DataFrame({
        "missing_count": prices.isna().sum(),
        "missing_pct": (prices.isna().mean() * 100).round(2),
        "first_valid_date": prices.apply(lambda s: s.first_valid_index()),
        "last_valid_date": prices.apply(lambda s: s.last_valid_index()),
    })
    missing_report.to_csv(OUTPUT_DIR / "data_quality_report.csv")
    print("\nData quality report (saved to outputs/data_quality_report.csv):")
    print(missing_report.to_string())

        # Preserve missing prices until returns have been calculated.
    # Dropping dates first could turn a multi-day return into a daily return.
    prices.to_csv(OUTPUT_DIR / "raw_downloaded_prices.csv")

    if len(prices.dropna(how="all")) <= TRAINING_DAYS + TEST_DAYS:
        raise RuntimeError("Insufficient price history for rolling backtesting.")

    return prices


def calculate_returns(prices):
    """Calculate daily returns without bridging missing-price gaps."""
    returns = prices.pct_change(fill_method=None)
    returns = returns.replace([np.inf, -np.inf], np.nan)
    returns = returns.dropna(how="any")

    if len(returns) <= TRAINING_DAYS:
        raise RuntimeError(
            "Insufficient complete daily returns for the training window."
        )

    returns.to_csv(OUTPUT_DIR / "daily_returns.csv")
    prices.loc[returns.index].to_csv(OUTPUT_DIR / "aligned_prices.csv")

    return returns

# ============================================================
# 3. PORTFOLIO CONSTRUCTION AND RISK METRICS
# ============================================================

def annualized_mean_return(daily_returns):
    """Arithmetic annualized return: mean daily simple return * 252."""
    return daily_returns.mean() * TRADING_DAYS


def annualized_volatility(daily_returns):
    """Annualized standard deviation of daily returns."""
    return daily_returns.std(ddof=1) * np.sqrt(TRADING_DAYS)


def sharpe_ratio(daily_returns, risk_free_rate=RISK_FREE_RATE):
    """Annualized Sharpe using daily excess returns and a compounded daily RF rate."""
    daily_rf = (1 + risk_free_rate) ** (1 / TRADING_DAYS) - 1
    excess = daily_returns - daily_rf
    vol = excess.std(ddof=1)
    if pd.isna(vol) or np.isclose(vol, 0):
        return np.nan
    return excess.mean() / vol * np.sqrt(TRADING_DAYS)


def sortino_ratio(daily_returns, risk_free_rate=RISK_FREE_RATE):
    """Annualized Sortino; downside deviation is RMS of returns below daily RF."""
    daily_rf = (1 + risk_free_rate) ** (1 / TRADING_DAYS) - 1
    excess = daily_returns - daily_rf
    downside = np.minimum(excess.to_numpy(), 0.0)
    downside_deviation = np.sqrt(np.mean(downside ** 2)) * np.sqrt(TRADING_DAYS)
    if np.isclose(downside_deviation, 0):
        return np.nan
    annualized_excess_mean = excess.mean() * TRADING_DAYS
    return annualized_excess_mean / downside_deviation


def historical_var_95(daily_returns):
    """Positive loss threshold: negative of the 5th percentile daily return."""
    return max(0.0, -float(np.nanpercentile(daily_returns, 5)))


def max_drawdown(daily_returns):
    """Worst peak-to-trough drawdown from a wealth index starting at 1."""
    wealth = (1 + daily_returns).cumprod()
    wealth = pd.concat([pd.Series([1.0]), wealth.reset_index(drop=True)], ignore_index=True)
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def performance_metrics(daily_returns):
    """Return comparable metrics for a daily return series."""
    r = pd.Series(daily_returns).dropna().astype(float)
    if r.empty:
        return {key: np.nan for key in [
            "Observations", "Total Return", "CAGR", "Annualized Arithmetic Return",
            "Annualized Volatility", "Sharpe Ratio", "Sortino Ratio",
            "Daily Historical VaR 95%", "Maximum Drawdown"
        ]}
    wealth = float((1 + r).prod())
    years = len(r) / TRADING_DAYS
    cagr = wealth ** (1 / years) - 1 if years > 0 and wealth > 0 else np.nan
    return {
        "Observations": int(len(r)),
        "Total Return": wealth - 1,
        "CAGR": cagr,
        "Annualized Arithmetic Return": float(r.mean() * TRADING_DAYS),
        "Annualized Volatility": float(r.std(ddof=1) * np.sqrt(TRADING_DAYS)),
        "Sharpe Ratio": sharpe_ratio(r),
        "Sortino Ratio": sortino_ratio(r),
        "Daily Historical VaR 95%": historical_var_95(r),
        "Maximum Drawdown": max_drawdown(r),
    }


def sample_portfolios(training_returns, n_portfolios=NUM_PORTFOLIOS):
    """Sample long-only fully invested portfolios and return max-Sharpe/min-vol weights."""
    assets = training_returns.columns.tolist()
    n_assets = len(assets)
    mean_returns = training_returns.mean().to_numpy() * TRADING_DAYS
    covariance = training_returns.cov().to_numpy() * TRADING_DAYS
    rf = RISK_FREE_RATE

    # Dirichlet draws guarantee nonnegative weights that sum to one.
    rng = np.random.default_rng(SEED)
    weights = rng.dirichlet(np.ones(n_assets), size=n_portfolios)
    p_returns = weights @ mean_returns
    p_variances = np.einsum("ij,jk,ik->i", weights, covariance, weights)
    p_volatility = np.sqrt(np.maximum(p_variances, 0))
    p_sharpe = np.divide(
        p_returns - rf, p_volatility,
        out=np.full_like(p_returns, np.nan), where=p_volatility > 0
    )

    if not np.isfinite(p_sharpe).any():
        raise RuntimeError("Unable to calculate valid Sharpe ratios for sampled portfolios.")

    max_sharpe_idx = int(np.nanargmax(p_sharpe))
    min_vol_idx = int(np.nanargmin(p_volatility))
    return {
        "Equal Weight": np.full(n_assets, 1 / n_assets),
        "Maximum Sharpe": weights[max_sharpe_idx],
        "Minimum Variance": weights[min_vol_idx],
    }, {
        "sampled_portfolios": n_portfolios,
        "sampled_max_sharpe": float(p_sharpe[max_sharpe_idx]),
        "sampled_min_volatility": float(p_volatility[min_vol_idx]),
    }

# ============================================================
# 4. ROLLING OUT-OF-SAMPLE BACKTEST
# ============================================================


def rolling_backtest(returns):
    """Fit weights on trailing data and test on the next unseen block."""
    asset_returns = returns[STOCKS].copy()
    benchmark_returns = returns[BENCHMARK].copy()

    strategy_names = [
        "Equal Weight",
        "Maximum Sharpe",
        "Minimum Variance",
    ]

    all_oos = {name: [] for name in strategy_names}
    all_oos["Nifty 50 Price Index"] = []

    weight_records = []
    window_records = []
    current_holdings = {name: None for name in strategy_names}
    cost_rate = TRANSACTION_COST_BPS / 10_000

    start = TRAINING_DAYS

    while start < len(asset_returns):
        end = min(start + TEST_DAYS, len(asset_returns))

        train = asset_returns.iloc[start - TRAINING_DAYS:start]
        test = asset_returns.iloc[start:end]

        weights_by_strategy, sampling_info = sample_portfolios(train)

        window_records.append({
            "train_start": str(train.index[0].date()),
            "train_end": str(train.index[-1].date()),
            "test_start": str(test.index[0].date()),
            "test_end": str(test.index[-1].date()),
            **sampling_info,
        })

        for name in strategy_names:
            target_weights = weights_by_strategy[name].copy()

            # Charge initial deployment cost once; subsequently charge
            # based on the change from actual drifted holdings to targets.
            old_holdings = current_holdings[name]

            if old_holdings is None:
                turnover = 1.0
            else:
                turnover = 0.5 * float(
                    np.abs(target_weights - old_holdings).sum()
                )

            holdings = target_weights.copy()
            net_daily_returns = []

            for i, (date, row) in enumerate(test.iterrows()):
                daily_asset_returns = row.to_numpy(dtype=float)

                # Holdings drift naturally between rebalancing dates.
                gross_return = float(
                    np.dot(holdings, daily_asset_returns)
                )

                net_return = gross_return

                # Apply the rebalance cost on the first day of this block.
                if i == 0:
                    net_return = (
                        (1 + gross_return) * (1 - cost_rate * turnover) - 1
                    )

                net_daily_returns.append(net_return)

                # Update actual portfolio weights after market movements.
                denominator = 1 + gross_return
                if denominator <= 0:
                    raise RuntimeError(
                        f"Invalid portfolio wealth on {date} for {name}."
                    )

                holdings = (
                    holdings * (1 + daily_asset_returns) / denominator
                )

            net_returns = pd.Series(
                net_daily_returns,
                index=test.index,
                name=name,
            )
            all_oos[name].append(net_returns)

            # Carry actual drifted holdings into the next rebalance.
            current_holdings[name] = holdings.copy()

            record = {
                "test_start": str(test.index[0].date()),
                "strategy": name,
                "turnover": turnover,
            }
            record.update({
                asset: float(weight)
                for asset, weight in zip(STOCKS, target_weights)
            })
            weight_records.append(record)

        # Nifty 50 price-index returns exclude reinvested dividends.
        all_oos["Nifty 50 Price Index"].append(
            benchmark_returns.loc[test.index]
        )

        start = end

    result = pd.DataFrame({
        name: pd.concat(parts).sort_index()
        for name, parts in all_oos.items()
        if parts
    })

    result = result[~result.index.duplicated(keep="first")]

    result.to_csv(
        OUTPUT_DIR / "rolling_oos_daily_returns.csv",
        index_label="Date",
    )
    pd.DataFrame(window_records).to_csv(
        OUTPUT_DIR / "rolling_windows.csv",
        index=False,
    )
    pd.DataFrame(weight_records).to_csv(
        OUTPUT_DIR / "rolling_portfolio_weights.csv",
        index=False,
    )

    return result


# ============================================================
# 5. REPORTING AND VISUALIZATION
# ============================================================

def create_results(oos_returns, asset_returns):
    metrics = pd.DataFrame({name: performance_metrics(oos_returns[name]) for name in oos_returns.columns}).T
    metrics.to_csv(OUTPUT_DIR / "rolling_oos_performance_summary.csv")

    print("\nROLLING OUT-OF-SAMPLE PERFORMANCE")
    print(f"Test period: {oos_returns.index.min().date()} to {oos_returns.index.max().date()}")
    print(f"Test observations: {len(oos_returns)}")
    print(f"Assumed transaction cost: {TRANSACTION_COST_BPS} bps; applied at each rebalance based on turnover")
    print("\nMetrics (returns/risks are decimals in the CSV; ratios are unitless):")
    print(metrics.round(4).to_string())

    wealth = (1 + oos_returns).cumprod()
    wealth.to_csv(OUTPUT_DIR / "rolling_oos_growth_of_1.csv", index_label="Date")

    plt.figure(figsize=(13, 7))
    for column in wealth.columns:
        plt.plot(wealth.index, wealth[column], label=column)
    plt.title("Rolling Out-of-Sample Growth of ₹1")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value (₹, before taxes; after assumed strategy transaction costs)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rolling_oos_growth.png", dpi=160)
    plt.close()

        # Include initial wealth of 1 so the chart matches max_drawdown().
    initial_date = wealth.index[0] - pd.Timedelta(days=1)

    initial_wealth = pd.DataFrame(
        [[1.0] * len(wealth.columns)],
        columns=wealth.columns,
        index=[initial_date],
    )

    wealth_with_initial = pd.concat([initial_wealth, wealth])
    drawdowns = (
        wealth_with_initial / wealth_with_initial.cummax()
    ) - 1
    
    plt.figure(figsize=(13, 6))
    for column in drawdowns.columns:
        plt.plot(drawdowns.index, drawdowns[column], label=column)
    plt.title("Rolling Out-of-Sample Drawdowns")
    plt.xlabel("Date")
    plt.ylabel("Drawdown from Previous Peak")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rolling_oos_drawdowns.png", dpi=160)
    plt.close()

        # Asset correlation over the full downloaded history.
    # Descriptive analysis only; not an out-of-sample performance metric.
    plt.figure(figsize=(12, 9))
    sns.heatmap(
        asset_returns[STOCKS].corr(),
        cmap="coolwarm",
        center=0
    )
    plt.title("Correlation Heatmap — NSE Equity Returns")
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "equity_correlation_heatmap.png",
        dpi=160
    )
    plt.close()

    print(f"\nOutputs saved in: {OUTPUT_DIR.resolve()}")
    print("Read methodology_notes.md before interpreting results.")


def main():
    prices = download_prices()
    returns = calculate_returns(prices)

    # Save the selected universe and run assumptions for reproducibility.
    settings = pd.Series({
        "stocks": ", ".join(STOCKS),
        "benchmark": BENCHMARK,
        "benchmark_definition": "Nifty 50 price index; not total return index (TRI)",
        "download_period": DOWNLOAD_PERIOD,
        "training_days": TRAINING_DAYS,
        "test_days": TEST_DAYS,
        "rebalancing": "Every 21 trading observations; weights fixed during each test block",
        "num_portfolios_per_window": NUM_PORTFOLIOS,
        "risk_free_rate_annual": RISK_FREE_RATE,
        "annualization_days": TRADING_DAYS,
        "transaction_cost_bps": TRANSACTION_COST_BPS,
        "random_seed": SEED,
        "missing_data_policy": "Drop dates with any missing value across all selected equities and benchmark; no forward fill",
        "weight_constraints": "Long-only; weights >= 0; weights sum to 1; no leverage",
    }, name="value")
    settings.to_csv(OUTPUT_DIR / "run_settings.csv", header=True)

    print(f"\nPrice data: {prices.index.min().date()} to {prices.index.max().date()}, {len(prices)} rows")
    print(f"Daily return data: {returns.index.min().date()} to {returns.index.max().date()}, {len(returns)} rows")
    print(f"Assets: {len(STOCKS)} equities + {BENCHMARK} benchmark")
    print(f"Training window: {TRAINING_DAYS} daily return observations; test/rebalance step: {TEST_DAYS}")

    oos_returns = rolling_backtest(returns)
    create_results(oos_returns, returns)


if __name__ == "__main__":
    main()
