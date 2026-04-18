from datetime import date

STOCKS = {
    "PETR4.SA": {"name": "Petrobras",     "color": "#009C3B"},
    "ITUB4.SA": {"name": "Itaú Unibanco", "color": "#003087"},
    "VALE3.SA": {"name": "Vale",           "color": "#C8963E"},
}

START_DATE = "2025-01-01"
END_DATE = date.today().strftime("%Y-%m-%d")
BENCHMARK_SYMBOL = "^BVSP"
BENCHMARK_NAME = "Ibovespa"
BENCHMARK_COLOR = "#888888"
