import streamlit as st
from sqlalchemy import text
from fetcher_service.db import get_db_session

st.set_page_config(page_title="Data Management", layout="wide")

st.title("🧮 Data Management — Crypto Strategy Engine")

# Recupera ultimo aggiornamento DB
session = get_db_session()
res = session.execute(text("SELECT value FROM meta WHERE key = 'last_updated'")).fetchone()
last_update = res[0] if res else "Mai eseguito"
session.close()

# Sidebar info e pulsante
st.sidebar.markdown(f"🕒 **Last DB update:** `{last_update}`")

with st.sidebar.expander("⚙️ Tools"):
    if st.button("🔄 Aggiorna ora il database"):
        st.warning("⚠️ Funzione non attiva: eseguire `auto_update.py` o attendere GitHub Action notturna.")

# Placeholder per estensioni future: upload CSV, quality, fill_missing
st.markdown("Questa sezione consente di gestire e aggiornare i dati storici delle crypto presenti nel database. Le funzionalità avanzate (caricamento CSV, qualità, integrazione fill_missing) saranno qui integrate.")
