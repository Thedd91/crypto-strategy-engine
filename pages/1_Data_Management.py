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

# Info DB
db_url = os.getenv("DATABASE_URL")
st.markdown(f"🔍 **URL DB in uso:** `{db_url}`")

# Sezione: Ultimo aggiornamento dal DB
session = get_db_session()
res = session.execute(text("SELECT value FROM meta WHERE key = 'last_updated'")).fetchone()
last_update = res[0] if res else "Mai eseguito"
session.close()
st.sidebar.markdown(f"🕒 **Last DB update:** `{last_update}`")

# Sezione: Pulsante aggiornamento manuale (placeholder)
with st.sidebar.expander("⚙️ Tools"):
    if st.button("🔄 Aggiorna ora il database"):
        st.warning("⚠️ Funzione non attiva: esegui `auto_update.py` o attendi GitHub Action notturna.")

# ─── Sezione 1: Fetch manuale di una singola coin ─────────────────────────────
st.header("📥 Fetch & Save manuale")
symbol = st.text_input("Inserisci simbolo coin (es. pepe, doge, wif)", "").lower()
if st.button("📊 Recupera e salva"):
    if not symbol:
        st.warning("⚠️ Inserisci prima un simbolo valido.")
    else:
        with st.spinner(f"🔍 Recupero dati per: {symbol}"):
            df = fetch_ohlcv(symbol, days=30)
            if df is not None and not df.empty:
                save_ohlcv(df, symbol)
                st.success(f"✅ {len(df)} righe salvate per {symbol}!")
            else:
                st.error("❌ Nessun dato trovato o errore API.")
st.markdown("---")

# ─── Sezione 2: Pulizia completa del database ─────────────────────────────────
st.header("🗑️ Pulizia completa del database")
st.markdown(
    "**Attenzione**: questa operazione **elimina TUTTI** i dati storici in `public.market_data`."
)
if st.button("🗑️ Svuota market_data"):
    if not st.checkbox("✅ Confermo di voler cancellare TUTTI i dati"):
        st.warning("☝️ Spunta la casella per confermare la cancellazione.")
    else:
        with st.spinner("Eliminazione dati in corso…"):
            clear_market_data()
        st.success("✅ Tabella `market_data` svuotata con successo!")
        st.experimental_rerun()
st.markdown("---")

# ─── Sezione 3: Bulk CSV Upload ───────────────────────────────────────────────
st.header("📂 Bulk CSV Upload")
st.markdown("Carica uno o più CSV storici dal tuo PC. Ogni file deve chiamarsi `<symbol>.csv`.")
uploaded_files = st.file_uploader(
    "Seleziona CSV storici",
    type="csv",
    accept_multiple_files=True
)
if uploaded_files:
    if st.button("🚀 Carica nel DB"):
        errors, results = [], []
        total = len(uploaded_files)
        progress = st.progress(0)
        with st.spinner("⏳ Importazione in corso…"):
            for idx, up in enumerate(uploaded_files, start=1):
                name = up.name.lower()
                symbol = name.split(".")[0]
                st.write(f"📄 Processo file `{name}` → simbolo `{symbol}`")
                try:
                    df = pd.read_csv(up, parse_dates=["snapped_at"], engine="python")
                except Exception as e:
                    errors.append(f"{name}: errore lettura CSV ({e})")
                    continue

                df = df.rename(columns={
                    "snapped_at": "timestamp",
                    "price": "close",
                    "total_volume": "volume"
                })
                df["open"] = df["close"]
                df["high"] = df["close"]
                df["low"]  = df["close"]
                df = df.set_index("timestamp")[["open","high","low","close","volume"]]

                try:
                    save_ohlcv(df, symbol)
                    results.append(f"{symbol}: {len(df)} righe importate")
                except Exception as e:
                    errors.append(f"{symbol}: errore salvataggio DB ({e})")

                progress.progress(int(idx / total * 100))

        st.success("📑 Import completato")
        for r in results:
            st.write("✅", r)
        for err in errors:
            st.error(err)
st.markdown("---")

# ─── Sezione 4: Data Quality Report ───────────────────────────────────────────
st.header("📊 Data Quality Report")
try:
    quality_df = get_quality_report()
    st.markdown(
        "- `completezza` = % di giorni rilevati vs giorni attesi  
"
        "- `missing_days` = giorni mancanti nel range  
"
        "- `score` = Alta / Media / Bassa"
    )
    st.dataframe(
        quality_df
        .sort_values(by="completezza", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=min(1000, 50 + 35 * len(quality_df))
    )

    st.markdown("### 📈 Profondità storica (anni) per coin")
    chart_df = quality_df.copy()
    chart_df["anni_storico"] = chart_df["periodo_totale"] / 365
    st.bar_chart(
        chart_df.set_index("symbol")[["anni_storico"]],
        use_container_width=True
    )
except Exception as e:
    st.error(f"❌ Errore nel calcolo della qualità dei dati: {e}")
