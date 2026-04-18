import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config import STOCKS, BENCHMARK_NAME, BENCHMARK_COLOR
from utils.formatters import format_brl, format_pct


def _stock_label(symbol: str) -> str:
    return STOCKS.get(symbol, {}).get("name", symbol)


def _stock_color(symbol: str) -> str:
    return STOCKS.get(symbol, {}).get("color", "#666666")


def build_normalized_performance_chart(
    normalized: pd.DataFrame,
    benchmark_series: pd.Series | None = None,
) -> go.Figure:
    fig = go.Figure()

    for symbol in normalized.columns:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[symbol],
            name=_stock_label(symbol),
            line=dict(color=_stock_color(symbol), width=2),
            hovertemplate=f"<b>{_stock_label(symbol)}</b><br>Data: %{{x|%d/%m/%Y}}<br>Performance: %{{y:.2f}}<extra></extra>",
        ))

    if benchmark_series is not None and not benchmark_series.empty:
        bench_norm = (benchmark_series / benchmark_series.iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=bench_norm.index,
            y=bench_norm,
            name=BENCHMARK_NAME,
            line=dict(color=BENCHMARK_COLOR, width=1.5, dash="dot"),
            hovertemplate=f"<b>{BENCHMARK_NAME}</b><br>Data: %{{x|%d/%m/%Y}}<br>Performance: %{{y:.2f}}<extra></extra>",
        ))

    fig.add_hline(y=100, line_dash="dash", line_color="gray", line_width=1, opacity=0.5)

    fig.update_layout(
        title="Performance Acumulada em 2025 (base 100 = 02/Jan/2025)",
        xaxis_title="Data",
        yaxis_title="Performance (base 100)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def build_price_history_chart(data: dict[str, pd.DataFrame]) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
        subplot_titles=("Preço de Fechamento (R$)", "Volume"),
    )

    for symbol, df in data.items():
        if df.empty or "Close" not in df.columns:
            continue
        label = _stock_label(symbol)
        color = _stock_color(symbol)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            name=label,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}<br>R$ %{{y:.2f}}<extra></extra>",
        ), row=1, col=1)

        if "Volume" in df.columns:
            fig.add_trace(go.Bar(
                x=df.index, y=df["Volume"],
                name=f"{label} Vol.",
                marker_color=color,
                opacity=0.5,
                showlegend=False,
                hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}<br>Vol: %{{y:,.0f}}<extra></extra>",
            ), row=2, col=1)

    fig.update_layout(
        title="Histórico de Preços e Volume em 2025",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis2=dict(rangeslider=dict(visible=True), type="date"),
    )
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def build_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    if df.empty:
        return go.Figure()

    label = _stock_label(symbol)
    color = _stock_color(symbol)

    close = df["Close"]
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=label,
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ))
    fig.add_trace(go.Scatter(x=df.index, y=sma20, name="SMA 20", line=dict(color="#f39c12", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=sma50, name="SMA 50", line=dict(color=color, width=1.5, dash="dot")))

    fig.update_layout(
        title=f"Candlestick — {label} 2025",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def build_monthly_returns_heatmap(data: dict[str, pd.DataFrame]) -> go.Figure:
    month_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    rows = []
    stock_names = []

    for symbol, df in data.items():
        if df.empty or "Close" not in df.columns:
            continue
        monthly = df["Close"].resample("ME").last().pct_change() * 100
        by_month = {m: None for m in range(1, 13)}
        for ts, val in monthly.items():
            by_month[ts.month] = round(val, 2)
        rows.append([by_month[m] for m in range(1, 13)])
        stock_names.append(_stock_label(symbol))

    if not rows:
        return go.Figure()

    import numpy as np
    z = [[v if v is not None else float("nan") for v in row] for row in rows]
    text = [[f"{v:.1f}%" if v is not None and not (isinstance(v, float) and v != v) else "" for v in row] for row in rows]

    fig = px.imshow(
        z,
        x=month_labels,
        y=stock_names,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text_auto=False,
        aspect="auto",
        title="Retornos Mensais (%) em 2025",
    )
    fig.update_traces(text=text, texttemplate="%{text}")
    fig.update_coloraxes(colorbar_title="Retorno %")
    return fig


def build_correlation_matrix(daily_returns: pd.DataFrame) -> go.Figure:
    if daily_returns.empty or daily_returns.shape[1] < 2:
        return go.Figure()

    renamed = daily_returns.rename(columns={s: _stock_label(s) for s in daily_returns.columns})
    corr = renamed.corr().round(3)

    fig = px.imshow(
        corr,
        color_continuous_scale="Blues",
        zmin=-1, zmax=1,
        text_auto=True,
        title="Correlação dos Retornos Diários",
        aspect="auto",
    )
    fig.update_coloraxes(colorbar_title="Correlação")
    return fig


def build_return_distribution_chart(daily_returns: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for symbol in daily_returns.columns:
        series = daily_returns[symbol].dropna()
        fig.add_trace(go.Histogram(
            x=series,
            name=_stock_label(symbol),
            marker_color=_stock_color(symbol),
            opacity=0.7,
            nbinsx=60,
            hovertemplate="Retorno: %{x:.2f}%<br>Frequência: %{y}<extra></extra>",
        ))
    fig.update_layout(
        barmode="overlay",
        title="Distribuição dos Retornos Diários em 2025",
        xaxis_title="Retorno Diário (%)",
        yaxis_title="Frequência",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
