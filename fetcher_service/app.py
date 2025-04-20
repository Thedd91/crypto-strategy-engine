# app.py (versione Streamlit della fetcher_service)
import streamlit as st
from fetch import fetch_ohlcv
from db import save_ohlcv

st.set_page_config(page_title="Crypto Fetcher", layout="centered")
st.title("🚀 Crypto Data Fetcher")

symbol = st.text_input("Inserisci il simbolo della coin (es. pepe, doge, wif)", value="pepe")
days = st.slider("Quanti giorni di storico vuoi scaricare?", min_value=1, max_value=90, value=30)

if st.button("Fetch & Save"): 
    with st.spinner("🔍 Recupero dati da CoinGecko..."):
        df = fetch_ohlcv(symbol, days)
        if df is not None:
            st.success(f"📊 Dati recuperati: {len(df)} righe")
            save_ohlcv(df, symbol)
            st.success("✅ Dati salvati nel database.")
            st.dataframe(df.tail())
        else:
            st.error("❌ Nessun dato trovato o errore nella risposta API")
