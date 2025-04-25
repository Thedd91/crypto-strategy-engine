# file: data_services/onchain_service/onchain_fetcher.py

import streamlit as st
import requests
import pandas as pd
import datetime
from data_services.utils.supabase_client import insert_into_metric_raw

# Dune Echo API settings
DUNE_API_URL = "https://api.dune.com/echo/v1"
DUNE_API_KEY = st.secrets["DUNE_API_KEY"]

HEADERS = {
    "x-dune-api-key": DUNE_API_KEY
}

# Chains to monitor
CHAINS = {
    "ethereum": "ethereum",
    "bsc": "bsc",
    "avalanche_c": "avalanche_c"
}

def fetch_active_addresses(chain: str) -> int:
    """
    Fetch active addresses count for a specific chain from Dune Echo.
    """
    try:
        url = f"{DUNE_API_URL}/transactions/{chain}"

        today = datetime.datetime.utcnow().isoformat() + "Z"

        params = {
            "after": today,
            "limit": 10000  # Max batch size
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

def run_onchain_fetcher():
    """
    Run the active addresses fetch across all chains and insert results into Supabase.
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
        insert_into_metric_raw(df)
    else:
        st.warning("⚠️ No active addresses data collected.")

