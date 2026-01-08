import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta,UTC
import math
import time
import warnings
warnings.filterwarnings('ignore')

LOOKBACK_DAYS    = 500      # fetch ~1y+ buffer
ROLL_DAYS_52W    = 252      # business days ~ 52 weeks
BREAKOUT_LOOK    = 10       # ~ last 2 calendar weeks
BREAKOUT_PCT     = 0.005    # 0.5% above prior 52w high
HIGH_NEAR_PCT    = 0.01     # within 1% of 52w high counts as "currently at/near"
VOL_MA_DAYS      = 20
VOL_MULT         = 1.5
TOP_N            = 100
BATCH_SIZE       = 80       # to avoid throttling
PAUSE_SEC        = 1.0


nifty500_csv="/Users/a0s0iro/PycharmProjects/Stock-Analysis-agent/files/ind_nifty500list.csv"
const = pd.read_csv(nifty500_csv)
symbols = const["Symbol"].dropna().astype(str).str.strip().unique().tolist()

tickers = [s + ".NS" for s in symbols]

def download_in_batches(tickers, period_days=LOOKBACK_DAYS, interval="1d"):
    all_data = {}
    start = (datetime.now(UTC) - timedelta(days=period_days)).date().isoformat()
    end = datetime.now(UTC).date().isoformat()
    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i:i+BATCH_SIZE]
        try:
            df = yf.download(batch, start=start, end=end, interval=interval, group_by='ticker', auto_adjust=False, threads=True, progress=False)
        except Exception as e:
            print(f"Batch error {i}:{i+len(batch)} -> {e}")
            time.sleep(PAUSE_SEC)
            continue
        # Normalize to dict of single-DF per ticker
        for t in batch:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    sub = df[t].dropna(how="all")
                else:
                    # single-ticker case
                    sub = df.copy()
                if not sub.empty:
                    all_data[t] = sub
            except KeyError:
                pass
        time.sleep(PAUSE_SEC)
    return all_data

def analyze(df):
    roll_high = df["Close"].rolling(ROLL_DAYS_52W, min_periods=ROLL_DAYS_52W).max()

    prior_high = roll_high.shift(1)

    recent = df.tail(180).copy()

    recent["breakout"] = recent["Close"] >= prior_high.loc[recent.index] * (1 + 0.01)

    breakoutDates = recent[recent.breakout]
    if len(breakoutDates) == 0:
        return {}

    rally_end_date = max(breakoutDates.index)
    rally_start_date = min(breakoutDates.index)

    rally_start_price = breakoutDates.loc[rally_start_date]["Close"]
    rally_end_price = breakoutDates.loc[rally_end_date]["Close"]

    last_high = pd.Timestamp.now() - rally_end_date

    gain_rally = float((rally_end_price - rally_start_price) / rally_start_price) * 100
    result = {}

    if gain_rally <= 30 and last_high <= pd.Timedelta(days=8):

        result = {
            "rallystart": rally_start_date,
            "rallyend": rally_end_date,
            "total_gain": gain_rally
        }

        for window in [360, 200, 100, 15]:
            if len(df) >= window:
                result[f"avg_vol_{window}d"] = df["Volume"].tail(window).mean()
            else:
                result[f"avg_vol_{window}d"] = df["Volume"].mean()
    return result

def get_momentum_stocks() ->list:
    """
     Returns a list of strong momentum stocks from the NIFTY 500 universe.

    This tool evaluates stocks based on predefined momentum criteria, such as
    price strength, trend persistence, and relative performance. It requires
    no input parameters and always returns an updated list of momentum stocks.

    Use this tool when:
    - The user requests "good stocks", "strong stocks", or "momentum stocks"
    - You need a screening list before deep technical analysis
    - You want to identify technically strong candidates for further analysis

    Returns:
        list[str]: A list of stock tickers demonstrating high momentum.
    """
    price_map = download_in_batches(tickers)
    rows = []
    for t, df in price_map.items():
        r = analyze(df)
        if not r:
            continue
        else:
            rows.append({"ticker": t, **r})
    return rows


