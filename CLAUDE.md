# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the app
streamlit run app.py

# Quick data pipeline smoke test
python3 -c "import yfinance as yf; print(yf.download('PETR4.SA', start='2025-01-01', progress=False).tail(3))"
```

The app runs at `http://localhost:8501` by default.

## Architecture

**Data flow:** `app.py` orchestrates everything — it calls `data/fetcher.py` to pull stock data from Yahoo Finance, passes DataFrames to `charts/builder.py` to build Plotly figures, and renders them via Streamlit tabs.

**Key design rules:**
- `data/fetcher.py` is the only module that calls `yfinance`. All functions there are decorated with `@st.cache_data(ttl=3600)`.
- `charts/builder.py` contains pure functions: they receive DataFrames and return `go.Figure` objects. No Streamlit calls inside.
- `components/` renders Streamlit UI widgets. `sidebar.py` returns a config dict; `metrics.py` renders KPI cards.
- `config.py` is the single source of truth for stock symbols, colors, and date range. Adding a new stock means editing only this file.

**B3-specific gotchas:**
- Tickers use the `.SA` suffix (e.g., `PETR4.SA`).
- yfinance returns timezone-aware DatetimeIndex for B3 data — call `.tz_localize(None)` after download.
- Jan 1 is a holiday; the normalization baseline (base 100) uses Jan 2 as the first trading day.
- Use `dropna(how="all")` to handle weekend/holiday gaps before passing data to chart builders.

**Stocks tracked:** Petrobras (`PETR4.SA`), Itaú Unibanco (`ITUB4.SA`), Vale (`VALE3.SA`). Benchmark overlay: Ibovespa (`^BVSP`).
