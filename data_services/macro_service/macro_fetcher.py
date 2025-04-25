# file: data_services/macro_service/macro_fetcher.py

import streamlit as st
import requests
import pandas as pd
from sqlalchemy import create_engine

# Load secrets from Streamlit
SUPABASE_CONN = st.secrets["SUPABASE_CONN"]

engine = create_engine(SUPABASE_CONN)

# Fear & Greed API Endpoint
FNG_API = "https://api.alternative.me/fng/"

def fetch_fng() -> pd.DataFrame:
    """Fetch the latest Fear & Greed Index."""
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

def save_to_db(df: pd.DataFrame):
    """Save the dataframe into metric_raw table."""
    if df.empty:
        st.warning("⚠️ No data to save.")
        return
    try:
        with engine.begin() as conn:
            df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
        st.success(f"✅ Saved {len(df)} rows to metric_raw.")
    except Exception as e:
        st.error(f"❌ Error saving to database: {e}")

def run_macro_fetcher():
    st.info("📡 Fetching Fear & Greed Index...")
    df = fetch_fng()
    if not df.empty:
        save_to_db(df)
    else:
        st.warning("⚠️ No data fetched.")

if __name__ == "__main__":
    run_macro_fetcher()
