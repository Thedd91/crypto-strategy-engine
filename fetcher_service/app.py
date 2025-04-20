# fetcher_service/app.py

import streamlit as st
import pandas as pd
from fetch import fetch_ohlcv
from db import save_ohlcv
from data_quality import get_quality_report
import os
st.write("🔍 URL DB in uso:", os.getenv("DATABASE_URL"))
st.set_page_config(page_title="Crypto Strategy Engine", layout="wide")

st.title("🚀 Crypto Strategy Engine")
st.markdown("Applicazione SaaS per importare e validare storici crypto")

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

# ─── Sezione 2: Bulk CSV Upload ────────────────────────────────────────────────
st.header("📂 Bulk CSV Upload")
st.markdown(
    """
    Carica uno o più CSV storici dal tuo PC (**una tantum**).
    Ogni file deve chiamarsi `<symbol>.csv` e avere colonne:
    - `snapped_at` (data)
    - `price`
    - `total_volume`
    """
)
uploaded_files = st.file_uploader(
    "Seleziona CSV storici",
    type="csv",
    accept_multiple_files=True
)
if uploaded_files:
    if st.button("🚀 Carica nel DB"):
        errors, results = [], []
        with st.spinner("Import in corso…"):
            for up in uploaded_files:
                name = up.name.lower()
                symbol = name.split(".")[0]
                try:
                    df = pd.read_csv(up, parse_dates=["snapped_at"])
                except Exception as e:
                    errors.append(f"{name}: errore lettura CSV ({e})")
                    continue

                # Rinomina e prepara DataFrame
                df = df.rename(columns={
                    "snapped_at": "timestamp",
                    "price":      "close",
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

        st.success("📑 Import completato")
        for r in results:  st.write("✅", r)
        for err in errors: st.error(err)

st.markdown("---")

# 🗑️ Sezione opzionale: Svuota completamente il database
st.markdown("---")
st.header("🗑️ Pulizia completa del database")

st.markdown(
    """
    **Attenzione**: questa operazione **elimina TUTTI** i dati storici
    in `public.market_data`.  
    ⁃ È irreversibile!  
    ⁃ Usare solo se vuoi ripartire da zero.
    """
)
if st.button("🗑️ Svuota market_data"):
    # checkbox di conferma
    if not st.checkbox("✅ Confermo di voler cancellare TUTTI i dati"):
        st.warning("☝️ Spunta la casella per abilitare il pulsante di cancellazione.")
    else:
        with st.spinner("Eliminazione dati in corso…"):
            from db import clear_market_data
            clear_market_data()
        st.success("✅ Tabella `market_data` svuotata con successo!")
# 🗑️ Sezione opzionale: Svuota completamente il database
st.markdown("---")
st.header("🗑️ Pulizia completa del database")

st.markdown(
    """
    **Attenzione**: questa operazione **elimina TUTTI** i dati storici
    in `public.market_data`.  
    ⁃ È irreversibile!  
    ⁃ Usare solo se vuoi ripartire da zero.
    """
)
if st.button("🗑️ Svuota market_data"):
    if not st.checkbox("✅ Confermo di voler cancellare TUTTI i dati"):
        st.warning("☝️ Spunta la casella per confermare la cancellazione.")
    else:
        with st.spinner("Eliminazione dati in corso…"):
            from db import clear_market_data
            clear_market_data()
        st.success("✅ Tabella `market_data` svuotata con successo!")
        st.experimental_rerun()  # ← qui: ricarica tutta l’app per aggiornare il Data Quality Report

# ─── Sezione 3: Data Quality Report ───────────────────────────────────────────
st.header("📊 Data Quality Report")
try:
    quality_df = get_quality_report()
    st.markdown(
        "Tabella della qualità dei dati storici per ciascun asset:\n"
        "- `completezza` = % di giorni rilevati vs giorni attesi\n"
        "- `missing_days` = giorni mancanti nel range\n"
        "- `score` = Alta / Media / Bassa\n"
    )
    st.dataframe(
        quality_df.sort_values(by="completezza", ascending=False),
        use_container_width=True
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
