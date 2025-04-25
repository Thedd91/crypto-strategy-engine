import streamlit as st

st.set_page_config(page_title="Strategie", layout="wide")

st.title("📈 Strategie — Crypto Strategy Engine")

st.markdown("""
Questa sezione ti permetterà di:
- Selezionare una coin e un intervallo temporale
- Scegliere una strategia (es. RSI Rebound, Breakout, Buy & Hold)
- Eseguire un backtest sui dati storici disponibili
- Visualizzare i risultati (equity curve, metriche di performance)

🛠️ Le strategie attualmente in sviluppo includono:
- RSI Rebound
- Breakout Optimizer
- Buy & Hold Benchmark
- Momentum + MA Crossover (in arrivo)
- Volume Surge (in arrivo)
""")
