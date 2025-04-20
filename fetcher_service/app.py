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
# 📦 Sezione Backfill storico (una tantum) con verifica post-run
import streamlit as st
from backfill import get_last_run_date, run_backfill, verify_backfill

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
                missing = verify_backfill()
            if not missing:
                st.success("🎉 Backfill completato e verificato: tutti i simboli hanno dati.")
            else:
                st.error(f"❌ Backfill completato ma mancano dati per: {', '.join(missing)}")
    else:
        with st.spinner("Esecuzione backfill in corso..."):
            run_backfill()
            missing = verify_backfill()
        if not missing:
            st.success("🎉 Backfill completato e verificato: tutti i simboli hanno dati.")
        else:
            st.error(f"❌ Backfill completato ma mancano dati per: {', '.join(missing)}")

# 🗑️ Sezione opzionale: svuota la tabella market_data (cancella TUTTI i dati)
import streamlit as st
from db import clear_market_data

st.markdown("---")
st.subheader("🗑️ Pulizia Database")

if st.button("🗑️ Svuota Tabella market_data"):
    # richiedi conferma esplicita
    if not st.checkbox("✅ Confermo di voler cancellare TUTTI i dati in market_data"):
        st.warning("☝️ Spunta la casella per confermare la cancellazione.")
    else:
        with st.spinner("Eliminazione dati in corso…"):
            clear_market_data()
        st.success("✅ Tabella market_data svuotata correttamente!")


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


# 📂 Sezione “Bulk CSV Upload” — carica multiple storiche direttamente da PC
# – Permette di selezionare uno o più file CSV
# – Per ogni file:
#     • Estrae il symbol dal nome (es. btc.csv → btc)
#     • Legge il CSV, rinomina le colonne “snapped_at” → “timestamp”, “price” → “close”, “total_volume” → “volume”
#     • Imposta open=high=low=close, poi chiama save_ohlcv()
# – Mostra spinner e log di avanzamento, e un riepilogo finale

st.markdown("---")
st.subheader("📥 Bulk CSV Upload")

uploaded_files = st.file_uploader(
    "Seleziona uno o più CSV storici",
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Carica nel DB"):
        import pandas as pd
        from db import save_ohlcv

        errors = []
        results = []
        with st.spinner("Import in corso…"):
            for up in uploaded_files:
                name = up.name.lower()
                symbol = name.split(".")[0]
                try:
                    df = pd.read_csv(up, parse_dates=["snapped_at"])
                except Exception as e:
                    errors.append(f"{name}: errore lettura CSV ({e})")
                    continue

                # Mappatura colonne CSV → schema market_data
                df = df.rename(columns={
                    "snapped_at": "timestamp",
                    "price":      "close",
                    "total_volume":"volume"
                })

                # open/high/low = close
                df["open"]  = df["close"]
                df["high"]  = df["close"]
                df["low"]   = df["close"]

                df = df.set_index("timestamp")
                df = df[["open","high","low","close","volume"]]

                try:
                    save_ohlcv(df, symbol)
                    results.append(f"{symbol}: {len(df)} righe importate")
                except Exception as e:
                    errors.append(f"{symbol}: errore salvataggio DB ({e})")

        # Mostra riepilogo
        st.success("📑 Import completato")
        for r in results:
            st.write("✅", r)
        for err in errors:
            st.error(err)
