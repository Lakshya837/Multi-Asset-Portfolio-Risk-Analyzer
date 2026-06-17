# Multi-Asset Portfolio Risk Analyzer

### Project Duration

**June 2026**

### Market Data Period

**19 June 2023 – 17 June 2026**

A quantitative finance and portfolio optimization project built in Python that analyzes risk, return, diversification, and portfolio construction across 15 NSE-listed equities using Modern Portfolio Theory (MPT), Monte Carlo simulation, and historical backtesting.

This project evaluates individual stocks and optimized portfolios using industry-standard risk metrics including Sharpe Ratio, Sortino Ratio, Value at Risk (VaR), and Maximum Drawdown.

---

## Project Highlights

* Analyzed **15 NSE-listed large-cap stocks** across Banking, IT, Energy, FMCG, Healthcare, Telecom, Automobile, and Consumer sectors.
* Processed **3 years of historical market data**.
* Calculated **740+ daily return observations** per asset.
* Evaluated portfolio risk and performance using **6 quantitative risk metrics**.
* Generated and analyzed **5,000 random portfolios** using Monte Carlo Simulation.
* Constructed:

  * Equal Weight Portfolio
  * Maximum Sharpe Portfolio
  * Minimum Variance Portfolio
* Built a complete **Efficient Frontier** visualization.
* Performed portfolio backtesting and cumulative performance analysis.
* Visualized portfolio allocations and diversification characteristics.

---

## Key Results

### Equal Weight Portfolio

| Metric            | Value  |
| ----------------- | ------ |
| Annual Return     | 9.36%  |
| Annual Volatility | 11.74% |
| Sharpe Ratio      | 0.29   |

### Maximum Sharpe Portfolio

| Metric            | Value  |
| ----------------- | ------ |
| Annual Return     | 15.36% |
| Annual Volatility | 12.47% |
| Sharpe Ratio      | 0.75   |

### Minimum Variance Portfolio

| Metric            | Value  |
| ----------------- | ------ |
| Annual Return     | 10.09% |
| Annual Volatility | 11.08% |
| Sharpe Ratio      | 0.37   |

### Portfolio Backtest Performance

Growth of ₹1 invested over the analysis period:

| Portfolio                  | Final Value |
| -------------------------- | ----------- |
| Equal Weight Portfolio     | ₹1.29       |
| Minimum Variance Portfolio | ₹1.32       |
| Maximum Sharpe Portfolio   | ₹1.53       |

Total Return Generated:

| Portfolio                  | Return |
| -------------------------- | ------ |
| Equal Weight Portfolio     | 29.01% |
| Minimum Variance Portfolio | 32.10% |
| Maximum Sharpe Portfolio   | 53.49% |

### Performance Insight

The Maximum Sharpe Portfolio generated the highest risk-adjusted return and outperformed both the Equal Weight Portfolio and the Minimum Variance Portfolio over the three-year backtesting period.

---

## Project Outcomes

* Evaluated 15 NSE equities using quantitative risk measures.
* Simulated 5,000 portfolios using Monte Carlo optimization.
* Identified optimal asset allocations using Modern Portfolio Theory.
* Achieved a backtested portfolio return of **53.49%** with the Maximum Sharpe Portfolio.
* Demonstrated the impact of diversification and risk-adjusted portfolio construction.
* Compared portfolio performance using historical backtesting.

---

## Risk Metrics Implemented

### Annualized Return

Measures expected yearly return based on average daily returns.

### Annualized Volatility

Measures annualized risk using the standard deviation of daily returns.

### Sharpe Ratio

Measures excess return earned per unit of total risk.

### Sortino Ratio

Measures excess return earned per unit of downside risk.

### Value at Risk (VaR 95%)

Estimates the worst expected daily loss at a 95% confidence level.

### Maximum Drawdown

Measures the largest peak-to-trough decline experienced during the analysis period.

---

## Portfolio Optimization Methodology

The project uses Monte Carlo Simulation to generate **5,000 random portfolio allocations**.

For each portfolio:

1. Portfolio weights are randomly generated.
2. Annualized return is calculated.
3. Annualized volatility is calculated.
4. Sharpe Ratio is computed.
5. Portfolio statistics are stored for comparison.

The simulation identifies:

### Maximum Sharpe Portfolio

Portfolio with the highest risk-adjusted return.

### Minimum Variance Portfolio

Portfolio with the lowest overall portfolio volatility.

---

## Visualizations

### Correlation Heatmap

Analyzes relationships among assets and identifies diversification opportunities.

### Efficient Frontier

Displays the risk-return characteristics of 5,000 simulated portfolios.

### Portfolio Allocation Charts

Pie chart visualization of:

* Maximum Sharpe Portfolio Allocation
* Minimum Variance Portfolio Allocation

### Portfolio Backtesting Performance

Comparison of cumulative growth for:

* Equal Weight Portfolio
* Minimum Variance Portfolio
* Maximum Sharpe Portfolio

---

## Dataset

### Source

Yahoo Finance (via yFinance API)

### Market Data Period

19 June 2023 – 17 June 2026

### Data Frequency

Daily

### Number of Assets

15 NSE-listed large-cap stocks

### Observations

* 741 Trading Days
* 740 Daily Return Observations

### Asset Universe

* Reliance Industries
* Tata Consultancy Services (TCS)
* Infosys
* HDFC Bank
* ICICI Bank
* State Bank of India (SBI)
* ITC
* Hindustan Unilever
* Sun Pharmaceutical Industries
* Dr. Reddy's Laboratories
* Asian Paints
* Maruti Suzuki
* Bharti Airtel
* ONGC
* Wipro

---

## Technology Stack

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* yFinance

---

## Concepts Demonstrated

* Modern Portfolio Theory (MPT)
* Portfolio Optimization
* Monte Carlo Simulation
* Quantitative Risk Analysis
* Risk-Adjusted Performance Measurement
* Diversification Analysis
* Efficient Frontier Construction
* Historical Portfolio Backtesting
* Financial Data Analysis
* Portfolio Allocation Optimization

---

## Repository Structure

```text
Multi_Asset_Portfolio_Risk_Analyser/
│
├── main.py
├── README.md
├── requirements.txt
├── screenshots/
│   ├── correlation_heatmap.png
│   ├── efficient_frontier.png
│   ├── max_sharpe_allocation.png
│   ├── min_variance_allocation.png
│   └── portfolio_backtest.png
│
└── .gitignore
```

---

## Future Improvements

* Black-Litterman Portfolio Optimization
* Conditional Value at Risk (CVaR)
* Rolling Window Backtesting
* Portfolio Rebalancing Strategies
* Factor-Based Investing Models
* Interactive Dashboard using Streamlit
* Live Market Data Integration

---

## Author

**Lakshya Kumar**

B.Tech, VLSI Design and Technology
National Institute of Technology Delhi


