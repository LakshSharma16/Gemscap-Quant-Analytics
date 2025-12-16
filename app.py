import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data import fetch_data
from analytics import (
    hedge_ratio, spread, zscore,
    rolling_corr, adf_pvalue
)

st.set_page_config(page_title="Quantitative Analytics Dashboard", layout="wide")

st.title("📊 Quantitative Analytics Dashboard")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
TIMEFRAMES = {
    "1s": "1s",
    "1m": "1m",
    "5m": "5m"
}

# ---------------- UI ----------------
c1, c2, c3 = st.columns(3)

sx = c1.selectbox("Symbol X", ["Select Symbol"] + SYMBOLS, key="sx")
sy = c2.selectbox("Symbol Y", ["Select Symbol"] + SYMBOLS, key="sy")
tf = c3.selectbox("Timeframe", list(TIMEFRAMES.keys()))

# ---------------- GUARDS ----------------
if sx == "Select Symbol" or sy == "Select Symbol":
    st.info("Please select both Symbol X and Symbol Y to start analytics.")
    st.stop()

if sx.strip().upper() == sy.strip().upper():
    st.warning(
        "Symbol X and Symbol Y are identical. "
        "Please select two different instruments."
    )
    st.stop()

# ---------------- DATA ----------------
with st.spinner("Fetching market data..."):
    dx = fetch_data(sx, TIMEFRAMES[tf])
    dy = fetch_data(sy, TIMEFRAMES[tf])

data = dx.join(dy, how="inner", lsuffix="_x", rsuffix="_y")
data.columns = ["X", "Y"]

if len(data) < 50:
    st.warning("Not enough data points for stable analytics.")
    st.stop()

# ---------------- ANALYTICS ----------------
hr = hedge_ratio(data["X"], data["Y"])
spr = spread(data["X"], data["Y"], hr)
z = zscore(spr)
corr = rolling_corr(data["X"], data["Y"])
pval = adf_pvalue(spr)

# ---------------- METRICS ----------------
m1, m2, m3, m4 = st.columns(4)

m1.metric("Hedge Ratio (OLS)", "N/A" if pd.isna(hr) else round(hr, 3))
m2.metric("ADF p-value", "N/A" if pd.isna(pval) else round(pval, 4))
m3.metric("Z-Score", "N/A" if z.dropna().empty else round(z.dropna().iloc[-1], 2))
m4.metric("Rolling Corr", "N/A" if corr.dropna().empty else round(corr.dropna().iloc[-1], 2))

# ---------------- PLOTS ----------------
def plot(series, title, key):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series, mode="lines"))
    fig.update_layout(title=title, height=300)
    st.plotly_chart(fig, use_container_width=True, key=key)

plot(data["X"], f"{sx} Price", "px")
plot(data["Y"], f"{sy} Price", "py")
plot(spr, "Spread", "spread")
plot(z, "Z-Score", "z")
plot(corr, "Rolling Correlation", "corr")
