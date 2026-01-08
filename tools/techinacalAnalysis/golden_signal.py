import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta,UTC
import math
import time
import warnings
warnings.filterwarnings('ignore')


def goldenSignalEntry(df, ticker):
    df = df.sort_index()
    price_col = "Close"
    df["SMA50"] = df[price_col].rolling(50, min_periods=50).mean()
    df["SMA200"] = df[price_col].rolling(200, min_periods=200).mean()
    df = df.dropna(subset=["SMA50", "SMA200"])
    cross_up = (df["SMA50"] > (df["SMA200"])) & (df["SMA50"].shift(2) <= df["SMA200"].shift(2))

    recent_window = df.index[-10:]
    recent_cross_dates = [ts for ts in df.index[cross_up] if ts in recent_window]
    if recent_cross_dates:
        ts = recent_cross_dates[-1]

        return {
            "ticker": ticker,
            "cross_date": ts,
            "close_on_cross": float(df.at[ts, price_col]),
            "sma50_on_cross": float(df.at[ts, "SMA50"]),
            "sma200_on_cross": float(df.at[ts, "SMA200"])
        }
def goldenSignalExit(df, ticker):
    df = df.sort_index()
    price_col = "Close"
    df["SMA50"] = df[price_col].rolling(50, min_periods=50).mean()
    df["SMA200"] = df[price_col].rolling(200, min_periods=200).mean()
    df = df.dropna(subset=["SMA50", "SMA200"])
    cross_up = (df["SMA50"] < (df["SMA200"])) & (df["SMA50"].shift(2) >= df["SMA200"].shift(2))

    recent_window = df.index[-10:]
    recent_cross_dates = [ts for ts in df.index[cross_up] if ts in recent_window]
    if recent_cross_dates:
        ts = recent_cross_dates[-1]

        return {
            "ticker": ticker,
            "cross_date": ts,
            "close_on_cross": float(df.at[ts, price_col]),
            "sma50_on_cross": float(df.at[ts, "SMA50"]),
            "sma200_on_cross": float(df.at[ts, "SMA200"])
        }


LOOKBACK_DAYS = 500
def download_in_batches(tickers, period_days=LOOKBACK_DAYS, interval="1d"):
      # fetch ~1y+ buffer
    ROLL_DAYS_52W = 252  # business days ~ 52 weeks
    BREAKOUT_LOOK = 10  # ~ last 2 calendar weeks
    BREAKOUT_PCT = 0.005  # 0.5% above prior 52w high
    HIGH_NEAR_PCT = 0.01  # within 1% of 52w high counts as "currently at/near"
    VOL_MA_DAYS = 20
    VOL_MULT = 1.5
    TOP_N = 100
    BATCH_SIZE = 80  # to avoid throttling
    PAUSE_SEC = 1.0
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



def golden_signal_entry() -> list:
    """
        Returns a list of stocks where the 50-day EMA has crossed ABOVE the
        200-day EMA, forming a bullish Golden Cross signal.

        This indicates long-term trend reversal or trend continuation strength,
        widely used by traders to identify strong bullish setups.

        Use this tool when:
        - User asks for “golden cross”, “bullish signal”, or “technical entry signals”
        - You want to find stocks with strong long-term uptrend confirmation

        Returns:
            list[str]: A list of stock tickers with a bullish golden cross.
    """
    nifty500_csv = "/Users/a0s0iro/PycharmProjects/Stock-Analysis-agent/files/ind_nifty500list.csv"

    const = pd.read_csv(nifty500_csv)
    symbols = const["Symbol"].dropna().astype(str).str.strip().unique().tolist()



    tickers = [s + ".NS" for s in symbols]
    price_map = download_in_batches(tickers)

    rows = []
    for t, df in price_map.items():
        r = goldenSignalEntry(df,t)
        if not r:
            continue
        else :
            rows.append({"ticker": t, **r})
    return rows

def golden_signal_exit() -> list:
    """
    Returns a list of stocks where the 50-day EMA has crossed BELOW the
    200-day EMA, forming a bearish Golden Cross Exit signal.

    This is considered a long-term bearish indicator and is used by traders
    to identify weakening trends or potential exit points.

    Use this tool when:
    - User asks for “bearish crossover”, “golden exit”, or weakening technical signals
    - Identifying potential sell or risk zones based on long-term moving averages

    Returns:
        list[str]: A list of stock tickers with a bearish golden cross exit signal.
    """
    nifty500_csv = "/Users/a0s0iro/PycharmProjects/Stock-Analysis-agent/files/ind_nifty500list.csv"

    const = pd.read_csv(nifty500_csv)
    symbols = const["Symbol"].dropna().astype(str).str.strip().unique().tolist()

    tickers = [s + ".NS" for s in symbols]
    price_map = download_in_batches(tickers)
    rows = []
    for t, df in price_map.items():
        r = goldenSignalExit(df,t)
        if not r:
            continue
        else :
            rows.append({"ticker": t, **r})
    return rows








