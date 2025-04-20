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


# 📦 Sezione opzionale per eseguire il backfill storico direttamente da Streamlit
# - Mostra la data dell’ultima esecuzione (dal file backfill_log.csv)
# - Protegge da click accidentali con una checkbox di conferma
# - Esegue run_backfill() una tantum per scaricare e salvare tutti i dati storici nel DB

import streamlit as st
from backfill import get_last_run_date, run_backfill

st.markdown("---")
st.subheader("📦 Backfill storico (una tantum)")

last_run = get_last_run_date()
if last_run:
    st.warning(f"⚠️ Il backfill è stato eseguito l'ultima volta il **{last_run}**")

if st.button("🔁 Esegui Backfill Storico"):
    if last_run:
        if not st.checkbox("✅ Confermo di voler eseguire nuovamente il backfill"):
            st.info("☝️ Spunta la casella per confermare.")
        else:
            with st.spinner("Esecuzione backfill in corso..."):
                run_backfill()
            st.success("✅ Backfill completato!")
    else:
        with st.spinner("Esecuzione backfill in corso..."):
            run_backfill()
        st.success("✅ Backfill completato!")

# 📊 Sezione di analisi della qualità dei dati storici per ciascun asset
# - Calcola completezza, range di date, giorni mancanti e score qualitativo
# - Mostra tabella interattiva filtrabile per score o completezza

from data_quality import get_quality_report

st.markdown("---")
st.subheader("📊 Data Quality Report")

try:
    quality_df = get_quality_report()

    st.markdown("Questa tabella mostra la qualità dei dati storici disponibili nel database per ciascun asset.")
    st.dataframe(
        quality_df.sort_values(by="completezza", ascending=False),
        use_container_width=True
    )

    # Grafico opzionale: profondità storica per coin
    st.markdown("### 📈 Anni di storico per coin")
    chart_df = quality_df.copy()
    chart_df["anni_storico"] = chart_df["periodo_totale"] / 365

    st.bar_chart(
        chart_df.set_index("symbol")[["anni_storico"]],
        use_container_width=True
    )

except Exception as e:
    st.error(f"❌ Errore nel calcolo della qualità dei dati: {e}")
