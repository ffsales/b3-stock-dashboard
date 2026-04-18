import streamlit as st
from datetime import datetime

from config import STOCKS, START_DATE, END_DATE
from data.fetcher import fetch_stock_data, fetch_benchmark, compute_normalized_returns, compute_daily_returns
from charts.builder import (
    build_normalized_performance_chart,
    build_price_history_chart,
    build_candlestick_chart,
    build_monthly_returns_heatmap,
    build_correlation_matrix,
    build_return_distribution_chart,
)
from components.sidebar import render_sidebar
from components.metrics import render_metric_cards

st.set_page_config(
    page_title="Dashboard de Ações 2025",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Dashboard de Ações Brasileiras — 2025")
st.caption(f"Petrobras · Itaú Unibanco · Vale &nbsp;|&nbsp; Período: 01/01/2025 a {datetime.now().strftime('%d/%m/%Y')}")

config = render_sidebar()
selected = tuple(config["selected_symbols"])

if not selected:
    st.warning("Selecione ao menos uma ação no painel lateral.")
    st.stop()

with st.spinner("Carregando dados..."):
    data = fetch_stock_data(selected)
    normalized = compute_normalized_returns(data)
    daily_returns = compute_daily_returns(data)
    benchmark_df = fetch_benchmark() if config["show_benchmark"] else None
    benchmark_series = benchmark_df["Close"] if benchmark_df is not None and not benchmark_df.empty else None

st.subheader("Resumo")
render_metric_cards(data, daily_returns)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Histórico de Preços", "Candlestick", "Análise"])

with tab1:
    fig = build_normalized_performance_chart(normalized, benchmark_series)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Base 100 = primeiro pregão de 2025 (02/Jan). Valores acima de 100 indicam valorização.")

with tab2:
    fig = build_price_history_chart(data)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    stock_options = {STOCKS[s]["name"]: s for s in selected if s in STOCKS}
    chosen_name = st.radio("Selecionar ação:", list(stock_options.keys()), horizontal=True)
    chosen_symbol = stock_options[chosen_name]
    fig = build_candlestick_chart(data[chosen_symbol], chosen_symbol)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("SMA 20 (laranja) e SMA 50 (pontilhada) calculadas sobre o preço de fechamento.")

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        fig = build_monthly_returns_heatmap(data)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = build_correlation_matrix(daily_returns)
        st.plotly_chart(fig, use_container_width=True)

    fig = build_return_distribution_chart(daily_returns)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Fonte: Yahoo Finance via yfinance · Os dados têm fins informativos e não constituem recomendação de investimento.")
