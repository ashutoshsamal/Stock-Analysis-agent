import yfinance as yf

# Only the useful financial fields

def get_fundamental_summary(ticker):
    """
   Fetches and returns essential fundamental information for a given stock
    using a yfinance-compatible ticker (e.g., 'RELIANCE.NS', 'TCS.NS').

    This tool is designed for LLM-based analysis and returns a structured,
    concise JSON containing only high-signal financial data. It includes:

    - Valuation metrics (PE, PB, Market Cap, ROE, Profit Margins, Dividend Yield)
    - Yearly income summary (Revenue, Profit, EPS, EBIT/EBITDA, etc.)
    - Quarterly income summary (same key fields)
    - Growth metrics (Revenue CAGR and Profit CAGR)

    The output is intentionally minimal and LLM-friendly, avoiding noisy or
    excessively detailed financial tables. It enables downstream agents to
    generate clear, reliable fundamental analysis reports.

    Parameters:
        ticker (str): A fully-qualified yfinance ticker string.

    Returns:
        dict: Structured fundamental data for use by an LLM agent.
    """
    USEFUL_FIELDS = [
        "Total Revenue",
        "Gross Profit",
        "Operating Income",
        "Net Income",
        "EBIT",
        "EBITDA",
        "Diluted EPS"
    ]

    stock = yf.Ticker(ticker)

    # -----------------------
    # Valuation Metrics
    # -----------------------
    info = stock.info
    valuation = {
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "market_cap": info.get("marketCap"),
        "dividend_yield": info.get("dividendYield"),
        "roe": info.get("returnOnEquity"),
        "profit_margin": info.get("profitMargins"),
    }

    # -----------------------
    # Helper: Extract clean financial fields
    # -----------------------
    def extract_financials(df):
        if df is None or df.empty:
            return None

        extracted = {}
        for field in USEFUL_FIELDS:
            if field in df.index:
                # Convert to clean dict: str(date) -> value
                series = df.loc[field].dropna()
                extracted[field] = {str(k.date()): float(v) for k, v in series.items()}
        return extracted

    yearly_income = extract_financials(stock.financials)
    quarterly_income = extract_financials(stock.quarterly_financials)

    # -----------------------
    # Growth Metrics (CAGR using yearly financials)
    # -----------------------
    def compute_cagr(series):
        try:
            if len(series) < 2:
                return None
            values = list(series.values())
            start, end = values[-1], values[0]
            years = len(values) - 1
            return ((end / start)**(1 / years) - 1) * 100
        except:
            return None

    growth = None
    try:
        revenue_series = yearly_income.get("Total Revenue")
        profit_series = yearly_income.get("Net Income")
        if revenue_series and profit_series:
            growth = {
                "revenue_cagr": compute_cagr(revenue_series),
                "profit_cagr": compute_cagr(profit_series),
            }
    except:
        pass

    # -----------------------
    # Final Output (LLM-Friendly)
    # -----------------------
    return {
        "ticker": ticker,
        "valuation": valuation,
        "financials": {
            "yearly": yearly_income,
            "quarterly": quarterly_income
        },
        "growth": growth
    }

