import streamlit as st
from config import STOCKS


def render_sidebar() -> dict:
    st.sidebar.title("Configurações")

    all_symbols = list(STOCKS.keys())
    all_names = [STOCKS[s]["name"] for s in all_symbols]

    selected_names = st.sidebar.multiselect(
        "Ações exibidas",
        options=all_names,
        default=all_names,
    )
    name_to_symbol = {v["name"]: k for k, v in STOCKS.items()}
    selected_symbols = [name_to_symbol[n] for n in selected_names if n in name_to_symbol]

    show_benchmark = st.sidebar.checkbox("Exibir Ibovespa como referência", value=True)

    st.sidebar.divider()
    if st.sidebar.button("Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.caption("Dados via Yahoo Finance · Atualização a cada 1h")

    return {
        "selected_symbols": selected_symbols,
        "show_benchmark": show_benchmark,
    }
