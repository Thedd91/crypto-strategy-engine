# file: data_services/utils/supabase_client.py

import streamlit as st
import requests
import pandas as pd

# Load secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_API_KEY = st.secrets["SUPABASE_API_KEY"]

def insert_into_metric_raw(df: pd.DataFrame):
    """
    Insert rows into the metric_raw table via Supabase REST API.
    """
    if df.empty:
        st.warning("⚠️ No data to insert.")
        return

    url = f"{SUPABASE_URL}/rest/v1/metric_raw"

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # --- 🔥 Convert Timestamp to ISO8601 strings
    if "ts" in df.columns:
        df["ts"] = df["ts"].apply(lambda x: x.isoformat() if pd.notnull(x) else None)

    # Convert DataFrame to list of dicts for JSON
    payload = df.to_dict(orient="records")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        st.success(f"✅ Inserted {len(payload)} rows into metric_raw.")
    except Exception as e:
        st.error(f"❌ Error inserting into Supabase: {e}")
