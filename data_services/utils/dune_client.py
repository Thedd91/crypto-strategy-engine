# file: data_services/utils/dune_client.py

import requests
import time
import pandas as pd
import streamlit as st

DUNE_API_URL = "https://api.dune.com/api/v1"
DUNE_API_KEY = st.secrets["DUNE_API_KEY"]

headers = {
    "X-Dune-API-Key": DUNE_API_KEY
}

def fetch_dune_query(query_id: int) -> pd.DataFrame:
    """Execute a Dune query and return the results as a DataFrame."""
    try:
        # Execute query
        exec_url = f"{DUNE_API_URL}/query/{query_id}/execute"
        exec_res = requests.post(exec_url, headers=headers)
        exec_res.raise_for_status()
        execution_id = exec_res.json()["execution_id"]

        # Wait for completion
        status_url = f"{DUNE_API_URL}/execution/{execution_id}/status"
        result_url = f"{DUNE_API_URL}/execution/{execution_id}/results"
        
        while True:
            status_res = requests.get(status_url, headers=headers)
            status_res.raise_for_status()
            state = status_res.json()["state"]
            if state == "QUERY_STATE_COMPLETED":
                break
            elif state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"):
                raise Exception(f"Dune query failed: {state}")
            time.sleep(2)

        # Fetch results
        result_res = requests.get(result_url, headers=headers)
        result_res.raise_for_status()
        rows = result_res.json()["result"]["rows"]
        
        return pd.DataFrame(rows)

    except Exception as e:
        st.error(f"❌ Dune fetch error: {e}")
        return pd.DataFrame()
