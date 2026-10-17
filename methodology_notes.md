# Portfolio Optimization & Risk Analytics — Methodology Notes

## Objective
Evaluate three long-only portfolio strategies using a rolling out-of-sample process and compare them with the Nifty 50 price index. The objective is methodological credibility, not a promise of outperformance.

## Portfolio universe and construction
- Equities: the 15 NSE-listed tickers defined in `main_upgraded.py`.
- Benchmark: Yahoo Finance ticker `^NSEI`, representing the Nifty 50 **price index**, not the Nifty 50 Total Return Index (TRI).
- Long-only constraint: all portfolio weights are nonnegative and sum to 1. No leverage, short selling, sector caps, or individual-asset caps are imposed.
- Equal Weight assigns `1 / number_of_assets` to each stock.
- Maximum Sharpe selects the highest estimated Sharpe ratio among 5,000 random portfolios sampled from a Dirichlet distribution.
- Minimum Variance selects the lowest estimated annualized volatility among the same sampled candidates.
- Monte Carlo selection is approximate: the selected portfolio is the best sampled candidate, not a guarantee of the global optimum.

## Rolling out-of-sample protocol
- Download up to five years of data to support more rolling windows.
- Use 252 trailing daily return observations as the training window.
- Re-estimate weights every 21 observations and hold those weights fixed for the next test block.
- Each test block occurs strictly after its training window. Test returns are not used to choose weights for that block.
- The reported performance is the concatenation of these test blocks, not the in-sample performance of the full history.

## Return and risk definitions
- Daily simple return: `P_t / P_(t-1) - 1`.
- Arithmetic annualized return: mean daily return multiplied by 252. This is not CAGR.
- CAGR: ending wealth raised to `252 / number_of_daily_observations`, minus 1.
- Annualized volatility: sample standard deviation of daily returns multiplied by `sqrt(252)`.
- Sharpe: mean daily excess return divided by its sample standard deviation, multiplied by `sqrt(252)`. Daily risk-free rate is derived from the 6% annual assumption.
- Sortino: annualized mean daily excess return divided by annualized downside deviation; downside deviation is the root mean square of negative daily excess returns relative to the daily risk-free target.
- Daily historical 95% VaR: negative of the 5th percentile daily return, floored at zero. It is a historical loss threshold, not a maximum-loss guarantee.
- Maximum drawdown: worst percentage decline from a previous wealth peak, including initial wealth of 1 as the starting peak.
- Total return: compounded growth over the measured period, minus 1.

## Data quality and limitations
- `auto_adjust=True` is used for equity price history. Corporate-action treatment depends on the data provider's adjusted series.
- Dates with missing prices in any selected equity or the benchmark are removed from the common calendar; prices are not forward-filled. This can shorten the sample and may induce selection effects.
- The selected 15-stock universe is fixed in advance and is not a point-in-time historical constituent universe. It may have survivorship/selection bias and does not represent all stocks available at each historical date.
- `^NSEI` is a price index and generally excludes reinvested dividends. Equity adjusted-price returns may reflect distributions, so this is not a perfectly like-for-like total-return comparison. A Nifty 50 TRI series would be preferable if reliable data is available.
- A flat 10 basis-point transaction-cost assumption is applied at each strategy rebalance using a documented turnover convention. It is a sensitivity assumption, not an estimate of actual brokerage, taxes, market impact, or liquidity costs. Taxes and slippage are not modeled separately.
- The annual risk-free rate is assumed to be 6% throughout the sample, rather than using a historical risk-free series.
- The optimizer estimates returns and covariance from a trailing window; estimation error can lead to unstable weights and poor subsequent performance.
- No claim is made that any strategy will outperform in the future. Past performance is not a forecast.

## Outputs
The script writes data-quality reports, aligned prices and returns, rolling windows, portfolio weights, out-of-sample daily returns, a performance summary, growth/drawdown charts, and run settings into the `outputs/` directory.
