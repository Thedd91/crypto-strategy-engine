# file: data_services/onchain_service/flow.py

import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Environment configurations
SUPABASE_CONN = os.getenv("SUPABASE_CONN")
GLASSNODE_KEY = os.getenv("GLASSNODE_KEY")
assert SUPABASE_CONN, "Missing SUPABASE_CONN in environment."
assert GLASSNODE_KEY, "Missing GLASSNODE_KEY in environment."

engine = create_engine(SUPABASE_CONN)

# Metric endpoints
METRICS = {
    "exchange_net_position_change": "transactions/exchange_net_position_change",
    "active_entities": "addresses/active_count",
    "supply_lth": "supply/supply_long_term_hodlers"
}

ASSETS = ["BTC", "ETH"]

BASE_URL = "https://api.glassnode.com/v1/metrics/"

def fetch_metric(metric: str, asset: str) -> pd.DataFrame:
    url = f"{BASE_URL}{METRICS[metric]}"
    params = {
        "a": asset,
        "api_key": GLASSNODE_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching {metric} for {asset}: {response.text}")
        return pd.DataFrame()
    data = response.json()
    df = pd.DataFrame(data)
    df["ts"] = pd.to_datetime(df["t"], unit="s")
    df["asset"] = asset
    df["metric"] = metric
    df["value"] = df["v"]
    df["src"] = "glassnode"
    df["meta"] = "{}"
    return df[["ts", "asset", "metric", "value", "src", "meta"]]

def save_to_db(df: pd.DataFrame):
    if df.empty:
        return
    with engine.begin() as conn:
        df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
    print(f"✅ Saved {len(df)} rows to metric_raw.")

if __name__ == "__main__":
    for metric in METRICS:
        for asset in ASSETS:
            print(f"Fetching {metric} for {asset}...")
            df = fetch_metric(metric, asset)
            save_to_db(df)
