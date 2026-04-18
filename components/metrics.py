import numpy as np
import streamlit as st
from config import STOCKS
from utils.formatters import format_brl, format_pct


def render_metric_cards(data: dict, daily_returns) -> None:
    symbols = [s for s in data if not data[s].empty]
    if not symbols:
        st.warning("Nenhum dado disponível para as ações selecionadas.")
        return

    cols = st.columns(len(symbols))
    for col, symbol in zip(cols, symbols):
        df = data[symbol]
        close = df["Close"].dropna()
        if close.empty:
            continue

        current_price = close.iloc[-1]
        ytd_return = ((close.iloc[-1] / close.iloc[0]) - 1) * 100

        rolling_max = close.cummax()
        drawdown = ((close - rolling_max) / rolling_max).min() * 100

        if symbol in daily_returns.columns:
            vol_30d = daily_returns[symbol].dropna().tail(30).std() * np.sqrt(252)
        else:
            vol_30d = float("nan")

        name = STOCKS[symbol]["name"]
        with col:
            st.metric(
                label=f"**{name}** ({symbol.replace('.SA', '')})",
                value=format_brl(current_price),
                delta=format_pct(ytd_return),
            )
            st.caption(
                f"Drawdown máx: {format_pct(drawdown)} &nbsp;|&nbsp; "
                f"Vol. 30d (anual.): {vol_30d:.1f}%"
            )
