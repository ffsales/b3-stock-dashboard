import pandas as pd
import yfinance as yf
import streamlit as st

from config import BENCHMARK_SYMBOL, START_DATE, END_DATE


@st.cache_data(ttl=3600)
def fetch_stock_data(symbols: tuple[str, ...], start: str = START_DATE, end: str = END_DATE) -> dict[str, pd.DataFrame]:
    raw = yf.download(list(symbols), start=start, end=end, auto_adjust=True, progress=False)
    result = {}
    for symbol in symbols:
        if len(symbols) == 1:
            df = raw.copy()
        else:
            df = raw.xs(symbol, axis=1, level=1) if symbol in raw.columns.get_level_values(1) else pd.DataFrame()
        df = df.dropna(how="all")
        if not df.empty and hasattr(df.index, "tz") and df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        result[symbol] = df
    return result


@st.cache_data(ttl=3600)
def fetch_benchmark(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    df = yf.download(BENCHMARK_SYMBOL, start=start, end=end, auto_adjust=True, progress=False)
    df = df.dropna(how="all")
    if not df.empty and hasattr(df.index, "tz") and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


def compute_normalized_returns(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = {}
    for symbol, df in data.items():
        if df.empty or "Close" not in df.columns:
            continue
        close = df["Close"].dropna()
        if close.empty:
            continue
        frames[symbol] = (close / close.iloc[0]) * 100
    return pd.DataFrame(frames)


def compute_daily_returns(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = {}
    for symbol, df in data.items():
        if df.empty or "Close" not in df.columns:
            continue
        frames[symbol] = df["Close"].pct_change().dropna() * 100
    return pd.DataFrame(frames)
