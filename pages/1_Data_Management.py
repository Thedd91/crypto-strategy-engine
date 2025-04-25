import os
import streamlit as st
import pandas as pd
from sqlalchemy import text

from fetcher_service.db import get_db_session
from fetcher_service.fetch import fetch_ohlcv
from fetcher_service.db import save_ohlcv, clear_market_data
from fetcher_service.data_quality import get_quality_report

st.set_page_config(page_title="Data Management", layout="wide")
st.title("🧮 Data Management — Crypto Strategy Engine")

db_url = os.getenv("DATABASE_URL")
st.markdown(f"🔍 **URL DB in uso:** `{db_url}`")

# Ultimo aggiornamento
session = get_db_session()
res = session.execute(text("SELECT value FROM meta WHERE key = 'last_updated'")).fetchone()
last_update = res[0] if res else "Mai eseguito"
session.close()
st.sidebar.markdown(f"🕒 **Last DB update:** `{last_update}`")

with st.sidebar.expander("⚙️ Tools"):
    if st.button("🔄 Aggiorna ora il database"):
        st.warning("⚠️ Funzione non attiva: esegui `auto_update.py` o attendi GitHub Action notturna.")

# Fetch manuale
st.header("📥 Fetch & Save manuale")
symbol = st.text_input("Inserisci simbolo coin", "").lower()
if st.button("📊 Recupera e salva"):
    if not symbol:
        st.warning("⚠️ Inserisci un simbolo valido.")
    else:
        with st.spinner(f"Recupero dati per {symbol}..."):
            df = fetch_ohlcv(symbol, days=30)
            if df is not None and not df.empty:
                save_ohlcv(df, symbol)
                st.success(f"✅ {len(df)} righe salvate per {symbol}")
            else:
                st.error("❌ Nessun dato trovato o errore API.")

# Pulizia DB
st.header("🗑️ Pulizia database")
if st.button("🧹 Svuota market_data"):
    if not st.checkbox("✅ Confermo di voler cancellare tutti i dati"):
        st.warning("☝️ Devi confermare la cancellazione.")
    else:
        with st.spinner("Eliminazione in corso..."):
            clear_market_data()
        st.success("✅ Tabella market_data svuotata!")

# Upload CSV
st.header("📂 Upload CSV storici")
uploaded_files = st.file_uploader("Carica CSV", type="csv", accept_multiple_files=True)
if uploaded_files:
    if st.button("🚀 Carica nel DB"):
        for file in uploaded_files:
            name = file.name
            symbol = name.split(".")[0]
            try:
                df = pd.read_csv(file, parse_dates=["snapped_at"])
                df = df.rename(columns={
                    "snapped_at": "timestamp",
                    "price": "close",
                    "total_volume": "volume"
                })
                df["open"] = df["close"]
                df["high"] = df["close"]
                df["low"] = df["close"]
                df = df.set_index("timestamp")[["open", "high", "low", "close", "volume"]]
                save_ohlcv(df, symbol)
                st.success(f"{symbol}: {len(df)} righe importate")
            except Exception as e:
                st.error(f"{symbol}: errore → {e}")

# Quality Report
st.header("📊 Data Quality Report")
try:
    quality_df = get_quality_report()
    st.dataframe(quality_df)
    st.bar_chart(
        quality_df.assign(anni_storico=quality_df["periodo_totale"] / 365)
        .set_index("symbol")[["anni_storico"]]
    )
except Exception as e:
    st.error(f"Errore nel quality report: {e}")
