# app.py (versione Streamlit della fetcher_service)
import streamlit as st
from fetch import fetch_ohlcv
from db import save_ohlcv
from init_db import create_table

st.set_page_config(page_title="Crypto Fetcher", layout="centered")
st.title("🚀 Crypto Data Fetcher")

# Bottone per creare la tabella nel DB
if st.button("🛠 Crea tabella DB"):
    with st.spinner("Creazione tabella nel database..."):
        try:
            create_table()
            st.success("✅ Tabella 'market_data' creata correttamente nel DB.")
        except Exception as e:
            st.error(f"❌ Errore nella creazione della tabella: {e}")

symbol = st.text_input("Inserisci il simbolo della coin (es. pepe, doge, wif)", value="pepe")
days = st.slider("Quanti giorni di storico vuoi scaricare?", min_value=1, max_value=90, value=30)

if st.button("Fetch & Save"): 
    with st.spinner("🔍 Recupero dati da CoinGecko..."):
        df = fetch_ohlcv(symbol, days)
        if df is not None:
            st.success(f"📊 Dati recuperati: {len(df)} righe")
            try:
                # Cast valori a float standard per evitare errori np.float64
                df = df.astype(float)
                save_ohlcv(df, symbol)
                st.success("✅ Dati salvati nel database.")
                st.dataframe(df.tail())
            except Exception as e:
                st.error(f"❌ Errore nel salvataggio: {e}")
        else:
            st.error("❌ Nessun dato trovato o errore nella risposta API")
