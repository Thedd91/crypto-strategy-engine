# file: data_services/onchain_service/onchain_fetcher.py

import streamlit as st
import requests
import pandas as pd
from sqlalchemy import create_engine
import datetime

# Load secrets
SUPABASE_CONN = st.secrets["SUPABASE_CONN"]
DUNE_API_KEY = st.secrets["DUNE_API_KEY"]

engine = create_engine(SUPABASE_CONN)

# Dune Echo API endpoint
ECHO_API_BASE = "https://api.dune.com/echo/v1"

# Headers for Dune Echo
HEADERS = {
    "x-dune-api-key": DUNE_API_KEY
}

# Chains che vogliamo monitorare
CHAINS = {
    "ethereum": "ethereum",
    "bsc": "bsc",
    "avalanche_c": "avalanche_c"
}

# Indirizzi noti di exchange da filtrare fuori (opzionale)
# EXCHANGE_ADDRESSES = ["0x...", "0x..."]  # Se vuoi evitare indirizzi CEX

def fetch_active_addresses(chain: str) -> int:
    """
    Fetch active addresses count for a specific chain from Dune Echo.
    """
    try:
        # Endpoint delle transazioni
        url = f"{ECHO_API_BASE}/transactions/{chain}"
        
        # Chiediamo solo l'ultimo giorno
        today = datetime.datetime.utcnow().isoformat() + "Z"

        params = {
            "after": today,  # o puoi non mettere after per tutto
            "limit": 10000  # massimo batch
        }

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        transactions = response.json().get("data", [])

        if not transactions:
            st.warning(f"⚠️ No transactions found for {chain}.")
            return 0

        addresses = set()

        for tx in transactions:
            from_addr = tx.get("from")
            if from_addr:
                addresses.add(from_addr.lower())

        return len(addresses)

    except Exception as e:
        st.error(f"❌ Error fetching active addresses on {chain}: {e}")
        return 0

def save_to_db(df: pd.DataFrame):
    """
    Save a DataFrame into metric_raw table.
    """
    if df.empty:
        st.warning("⚠️ No data to save.")
        return

    try:
        with engine.begin() as conn:
            df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
        st.success(f"✅ Saved {len(df)} rows to metric_raw.")
    except Exception as e:
        st.error(f"❌ Error saving to database: {e}")

def run_onchain_fetcher():
    """
    Run active addresses fetch across all chains and save results.
    """
    st.info("🚀 Fetching Active Addresses from Dune Echo API...")

    records = []
    now = pd.Timestamp.utcnow()

    for chain_name, chain_key in CHAINS.items():
        st.info(f"📡 Fetching for {chain_name}...")
        active_count = fetch_active_addresses(chain_key)
        if active_count > 0:
            record = {
                "ts": now,
                "asset": chain_name,
                "metric": "active_addresses",
                "value": active_count,
                "src": "dune_echo",
                "meta": "{}"
            }
            records.append(record)

    if records:
        df = pd.DataFrame(records)
        save_to_db(df)
    else:
        st.warning("⚠️ No active addresses data collected.")

if __name__ == "__main__":
    run_onchain_fetcher()
