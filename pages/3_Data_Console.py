# file: pages/3_Data_Console.py

import streamlit as st
import sys
from pathlib import Path
from graphviz import Digraph

# Extend path to include services
sys.path.append(str(Path(__file__).parent.parent))

# Import fetchers
from data_services.onchain_service.flow import run_onchain_fetcher
from data_services.macro_service.macro_fetcher import run_macro_fetcher
from data_services.onchain_service.dune_fetcher import run_dune_fetcher

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Data Console", layout="wide")
st.title("🛠️ Data Console")
st.markdown("Gestisci i micro-servizi di raccolta dati alternativi.")

st.divider()

# --- SERVICE CONTROL PANEL ---
st.header("🔧 Controllo Servizi Dati")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💾 Onchain Service (Flow)")
    if st.button("📡 Run Onchain Fetcher"):
        with st.spinner("Fetching Onchain Data..."):
            run_onchain_fetcher()

with col2:
    st.subheader("🌐 Macro Service (Fear & Greed)")
    if st.button("🌐 Run Macro Fetcher"):
        with st.spinner("Fetching Macro Data..."):
            run_macro_fetcher()

with col3:
    st.subheader("🔷 Dune Analytics Fetcher")
    if st.button("📡 Run Dune Fetcher"):
        with st.spinner("Executing Dune Query..."):
            run_dune_fetcher()

st.divider()

# --- ARCHITECTURE MAP ---
st.header("🗺️ Architettura Dati")

dot = Digraph("CryptoStrategyEngine", format="png")
dot.attr(rankdir="LR", size="10")

# Services
dot.node("A", "OHLCV Price Data\n(fetcher_service)")
dot.node("B", "Onchain Flow\n(onchain_service)")
dot.node("C", "Macro Sentiment\n(macro_service)")
dot.node("D", "Dune Queries\n(onchain_service)")

# Central Database
dot.node("DB", "Supabase\n(metric_raw, price_ohlcv)")

# Feature Lab and Strategies
dot.node("FL", "Feature Lab")
dot.node("STRAT", "Strategies & Agent")

# Links
dot.edge("A", "DB")
dot.edge("B", "DB")
dot.edge("C", "DB")
dot.edge("D", "DB")
dot.edge("DB", "FL")
dot.edge("FL", "STRAT")

# Draw the graph
st.graphviz_chart(dot)

st.divider()
st.markdown("🔵 Powered by Supabase · Streamlit · Python · Dune · Crypto APIs")
