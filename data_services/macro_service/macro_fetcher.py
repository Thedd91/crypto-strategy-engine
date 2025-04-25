# file: data_services/macro_service/macro_fetcher.py

import streamlit as st
import requests
import pandas as pd
from data_services.utils.supabase_client import insert_into_metric_raw

# Fear & Greed Index API endpoint
FNG_API = "https://api.alternative.me/fng/"

def fetch_fng() -> pd.DataFrame:
    """
    Fetch the latest Fear & Greed Index and prepare DataFrame.
    """
    try:
        res = requests.get(FNG_API, timeout=10)
        res.raise_for_status()
        data = res.json()["data"]
        df = pd.DataFrame(data)
        df["ts"] = pd.to_datetime(df["timestamp"], unit="s")
        df["asset"] = "CRYPTO"
        df["metric"] = "fear_greed_index"
        df["value"] = pd.to_numeric(df["value"])
        df["src"] = "alternative.me"
        df["meta"] = "{}"
        return df[["ts", "asset", "metric", "value", "src", "meta"]]
    except Exception as e:
        st.error(f"❌ Error fetching Fear & Greed Index: {e}")
        return pd.DataFrame()

def run_macro_fetcher():
    """
    Run the macro fetcher and insert data into Supabase.
    """
    st.info("🌐 Fetching Fear & Greed Index...")
    df = fetch_fng()
    if not df.empty:
        insert_into_metric_raw(df)
    else:
        st.warning("⚠️ No data fetched to insert.")
