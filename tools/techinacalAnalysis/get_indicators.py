import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta,UTC
import math
import time
import warnings
warnings.filterwarnings('ignore')
def fetch_price_data(ticker, period="6mo", interval="1d"):
    """
    Fetch OHLCV data using yfinance.
    """
    df = yf.download(ticker, period=period, interval=interval)
    df = df.dropna()
    return df

def rma(series, period):
    return series.ewm(alpha=1/period, adjust=False).mean()

################################################## ADX:- #####################################################
def compute_adx(high, low, close, period=14):
    # FORCE inputs to 1-D arrays → fixes your error
    high = pd.Series(np.array(high).reshape(-1)).astype(float)
    low = pd.Series(np.array(low).reshape(-1)).astype(float)
    close = pd.Series(np.array(close).reshape(-1)).astype(float)

    # True Range
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Wilder smoothing (TradingView style)
    tr_rma = rma(tr, period)
    plus_dm_rma = rma(pd.Series(plus_dm), period)
    minus_dm_rma = rma(pd.Series(minus_dm), period)

    plus_di = 100 * (plus_dm_rma / tr_rma)
    minus_di = 100 * (minus_dm_rma / tr_rma)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    adx = rma(dx, period)  # ADX = RMA of DX

    return float(adx.dropna().iloc[-1])

################################################## RSI:- #####################################################
def compute_rsi(close_prices, period=14):
    close = pd.Series(np.array(close_prices).reshape(-1)).astype(float)

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = rma(gain, period)
    avg_loss = rma(loss, period)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


################################################## MACD:- #####################################################
def compute_macd(close_prices, fast=12, slow=26, signal=9):
    # Ensure 1D input
    close = pd.Series(np.array(close_prices).reshape(-1)).astype(float)

    # TradingView EMA (standard EMA)
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    # Extract numeric values
    prev_macd = float(macd_line.iloc[-2])
    prev_signal = float(signal_line.iloc[-2])
    prev_hist = float(histogram.iloc[-2])

    curr_macd = float(macd_line.iloc[-1])
    curr_signal = float(signal_line.iloc[-1])
    curr_hist = float(histogram.iloc[-1])

    # --------------------------
    # TREND (Ongoing)
    # --------------------------
    if curr_macd > curr_signal:
        trend = "bullish"
    else:
        trend = "bearish"

    # --------------------------
    # CROSSOVER (Event)
    # --------------------------
    if prev_macd < prev_signal and curr_macd > curr_signal:
        crossover = "bullish"
    elif prev_macd > prev_signal and curr_macd < curr_signal:
        crossover = "bearish"
    else:
        crossover = "none"

    # --------------------------
    # HISTOGRAM MOMENTUM (Strength)
    # --------------------------
    if curr_hist > prev_hist:
        momentum = "increasing"
    elif curr_hist < prev_hist:
        momentum = "decreasing"
    else:
        momentum = "flat"

    # --------------------------
    # RETURN STRUCTURED OUTPUT
    # --------------------------
    return {
        "macd_value": curr_macd,
        "signal_value": curr_signal,
        "histogram_value": curr_hist,

        # Trend classification:
        "trend": trend,                 # bullish or bearish

        # Crossover classification:
        "crossover": crossover,         # bullish / bearish / none

        # Momentum classification:
        "momentum": momentum,           # increasing / decreasing / flat

        # Raw previous values (agent can infer patterns)
        "previous_macd": prev_macd,
        "previous_signal": prev_signal,
        "previous_histogram": prev_hist
    }

################################################## Volume:- #####################################################
def compute_volume_indicator(volume):
    # Force volume into 1D Series
    volume = pd.Series(np.array(volume).reshape(-1))

    avg_20 = volume.rolling(20).mean()

    last_volume = float(volume.iloc[-1])
    avg_20_volume = float(avg_20.iloc[-1])

    trend = "High" if last_volume > avg_20_volume else "Low"

    return {
        "last_volume": last_volume,
        "avg_20_volume": avg_20_volume,
        "volume_trend": trend
    }

################################################## EMA:- #####################################################
def compute_ema(close_prices, period=20):
    return close_prices.ewm(span=period, adjust=False).mean().iloc[-1]

################################################## BOLLINGER_BAND:- #####################################################
def compute_bollinger_bands(close_prices, length=20, std_dev=2, squeeze_threshold=0.025):
    # Ensure 1D input
    close = pd.Series(np.array(close_prices).reshape(-1)).astype(float)

    # Middle band = SMA
    middle = close.rolling(length).mean()

    # Standard deviation
    std = close.rolling(length).std()

    # Upper & lower bands
    upper = middle + std_dev * std
    lower = middle - std_dev * std

    # Latest values (convert to float)
    upper_val = float(upper.iloc[-1])
    middle_val = float(middle.iloc[-1])
    lower_val = float(lower.iloc[-1])

    # Band width % relative to price
    bandwidth = (upper_val - lower_val) / middle_val

    # ----------------------
    # SQUEEZE DETECTION
    # ----------------------
    squeeze = bandwidth < squeeze_threshold

    # Expansion: Squeeze ended recently and now bandwidth increasing
    prev_bandwidth = (upper.iloc[-2] - lower.iloc[-2]) / middle.iloc[-2]
    expansion = (prev_bandwidth < squeeze_threshold) and (bandwidth > prev_bandwidth)

    # Return structured data
    return {
        "upper_band": upper_val,
        "middle_band": middle_val,
        "lower_band": lower_val,
        "bandwidth": float(bandwidth),

        "squeeze": bool(squeeze),       # low volatility
        "expansion": bool(expansion),   # volatility breakout

        "previous_upper": float(upper.iloc[-2]),
        "previous_middle": float(middle.iloc[-2]),
        "previous_lower": float(lower.iloc[-2]),
        "previous_bandwidth": float(prev_bandwidth)
    }


################################################## MAIN:- #####################################################
def get_indicator(ticker, indicator=None, period=14, yf_period="6mo", yf_interval="1d"):
    """
    Computes one or all technical indicators for a given stock.
    The ticker must be a valid, fully-qualified yfinance symbol
    (e.g., 'RELIANCE.NS', 'KIRLOSBROS.NS').

    If `indicator` is None → returns ALL supported indicators.
    If an indicator name is provided → returns only that indicator.

    Supported indicators:
        RSI, ADX, EMA, MACD, VOLUME, BOLLINGER_BAND
    """

    df = fetch_price_data(ticker, period=yf_period, interval=yf_interval)

    # Normalize
    indicator = indicator.upper() if indicator else None

    # --- Helper functions mapped to keys ---
    def compute_all():
        return {
            "RSI": float(compute_rsi(df["Close"], period)),
            "ADX": float(compute_adx(df["High"], df["Low"], df["Close"], period)),
            "EMA": f"EMA for the period {period} is :- "+str(compute_ema(df["Close"], period)),
            "MACD": compute_macd(df["Close"]),  # returns dict
            "VOLUME": compute_volume_indicator(df["Volume"]),
            "BOLLINGER_BAND": compute_bollinger_bands(df["Close"])
        }

    # If indicator is not provided → return ALL indicators
    if indicator is None:
        result = compute_all()
        return {
            "ticker": ticker,
            "indicators": result,
            "message": "Returned all indicators for this ticker."
        }

    # If only ONE indicator is asked for
    if indicator == "RSI":
        return {"indicator": "RSI", "value": float(compute_rsi(df["Close"], period))}

    elif indicator == "ADX":
        return {"indicator": "ADX", "value": float(compute_adx(df["High"], df["Low"], df["Close"], period))}

    elif indicator == "EMA":
        return {"indicator": "EMA", "value": float(compute_ema(df["Close"], period))}

    elif indicator == "MACD":
        return {"indicator": "MACD", **compute_macd(df["Close"])}

    elif indicator == "VOLUME":
        return {"indicator": "VOLUME", **compute_volume_indicator(df["Volume"])}

    elif indicator == "BOLLINGER_BAND":
        return {"indicator": "BOLLINGER_BAND", **compute_bollinger_bands(df["Close"])}

    else:
        return {"error": f"Unknown indicator requested: {indicator}"}



