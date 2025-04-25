# file: data_services/onchain_service/dune_fetcher.py

import streamlit as st
import requests
import pandas as pd
import time
from sqlalchemy import create_engine

# Load secrets
SUPABASE_CONN = st.secrets["SUPABASE_CONN"]
DUNE_API_KEY = st.secrets["DUNE_API_KEY"]

engine = create_engine(SUPABASE_CONN)

DUNE_API_URL = "https://api.dune.com/api/v1"
QUERY_ID = 5039959  # tuo Query ID

headers = {
    "X-Dune-API-Key": DUNE_API_KEY
}

def execute_query() -> str:
    """Start query execution and return execution_id."""
    url = f"{DUNE_API_URL}/query/{QUERY_ID}/execute"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    execution_id = response.json()["execution_id"]
    return execution_id

def wait_for_completion(execution_id: str) -> dict:
    """Wait until the query execution is completed."""
    status_url = f"{DUNE_API_URL}/execution/{execution_id}/status"
    result_url = f"{DUNE_API_URL}/execution/{execution_id}/results"

    while True:
        res = requests.get(status_url, headers=headers)
        res.raise_for_status()
        state = res.json()["state"]
        if state == "QUERY_STATE_COMPLETED":
            break
        elif state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"):
            raise Exception(f"Query failed with state {state}")
        time.sleep(2)  # wait before checking again

    result = requests.get(result_url, headers=headers)
    result.raise_for_status()
    return result.json()

def save_to_db(df: pd.DataFrame):
    """Save the DataFrame into the metric_raw table."""
    if df.empty:
        st.warning("⚠️ No data fetched.")
        return
    try:
        with engine.begin() as conn:
            df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
        st.success(f"✅ Saved {len(df)} rows to metric_raw.")
    except Exception as e:
        st.error(f"❌ Error saving to database: {e}")

def run_dune_fetcher():
    """Run the full Dune query fetch and save."""
    try:
        st.info("🚀 Starting Dune query execution...")
        execution_id = execute_query()
        st.info(f"⏳ Waiting for execution_id {execution_id} to complete...")
        result = wait_for_completion(execution_id)

        # Parse result into DataFrame
        rows = result["result"]["rows"]
        if not rows:
            st.warning("⚠️ No rows returned from Dune.")
            return

        df = pd.DataFrame(rows)
        
        # Adjust these fields based on your query output structure
        df["ts"] = pd.Timestamp.utcnow()
        df["asset"] = "ETH"  # o modificabile in base all'asset reale
        df["metric"] = "tx_count"  # es: numero di transazioni ultime 24h
        df["value"] = df["tx_count"]  # se nella tua query hai una colonna tx_count
        df["src"] = "dune"
        df["meta"] = "{}"

        save_to_db(df[["ts", "asset", "metric", "value", "src", "meta"]])

    except Exception as e:
        st.error(f"❌ Dune fetcher failed: {e}")

if __name__ == "__main__":
    run_dune_fetcher()
