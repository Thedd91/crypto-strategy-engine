# file: pages/3_Data_Console.py

import streamlit as st
import sys
from pathlib import Path
from graphviz import Digraph
import pandas as pd
from sqlalchemy import create_engine

# Extend path to include services
sys.path.append(str(Path(__file__).parent.parent))

# Import fetchers
from data_services.macro_service.macro_fetcher import run_macro_fetcher
from data_services.onchain_service.onchain_fetcher import run_onchain_fetcher

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Data Console", layout="wide")
st.title("🛠️ Data Console")
st.markdown("Controlla e gestisci i microservizi di raccolta dati alternativi.")

st.divider()

# --- SERVICE CONTROL PANEL ---
st.header("🔧 Controllo Servizi Dati")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Macro Service (Fear & Greed Index)")
    if st.button("🌐 Run Macro Fetcher"):
        with st.spinner("Fetching Macro Data..."):
            run_macro_fetcher()

with col2:
    st.subheader("📡 Onchain Service (Active Addresses - Echo API)")
    if st.button("📡 Run Onchain Fetcher"):
        with st.spinner("Fetching Active Addresses from Echo API..."):
            run_onchain_fetcher()

st.divider()

# --- ARCHITECTURE MAP ---
st.header("🗺️ Architettura Dati")

dot = Digraph("CryptoStrategyEngine", format="png")
dot.attr(rankdir="LR", size="10")

# Services
dot.node("OHLCV", "OHLCV Price Data\n(fetcher_service)")
dot.node("Macro", "Macro Sentiment\n(macro_service)")
dot.node("OnChain", "Onchain Active Addresses\n(onchain_service)")

# Central Database
dot.node("DB", "Supabase\n(metric_raw, price_ohlcv)")

# Feature Lab and Strategies
dot.node("FL", "Feature Lab")
dot.node("STRAT", "Strategies & Agent")

# Links
dot.edge("OHLCV", "DB")
dot.edge("Macro", "DB")
dot.edge("OnChain", "DB")
dot.edge("DB", "FL")
dot.edge("FL", "STRAT")

st.graphviz_chart(dot)

st.divider()

# --- METRIC RAW PREVIEW ---
st.header("🔍 Anteprima Tabella metric_raw")

# Load connection
SUPABASE_CONN = st.secrets["SUPABASE_CONN"]
engine = create_engine(SUPABASE_CONN)

try:
    df = pd.read_sql("SELECT * FROM metric_raw ORDER BY ts DESC LIMIT 50", con=engine)
    st.dataframe(df)
except Exception as e:
    st.error(f"❌ Error loading metric_raw preview: {e}")

st.divider()
st.markdown("🔵 Powered by Supabase · Streamlit · Python · Dune Echo API")
