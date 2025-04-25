# file: data_services/onchain_service/flow.py

import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment
load_dotenv()

SUPABASE_CONN = os.getenv("SUPABASE_CONN")
GLASSNODE_KEY = os.getenv("GLASSNODE_KEY")
assert SUPABASE_CONN, "Missing SUPABASE_CONN"
assert GLASSNODE_KEY, "Missing GLASSNODE_KEY"

engine = create_engine(SUPABASE_CONN)

# Define metrics and their API paths
METRICS = {
    "exchange_net_position_change": "transactions/exchange_net_position_change",
    "active_entities": "addresses/active_count",
    "supply_lth": "supply/supply_long_term_hodlers"
}

ASSETS = ["BTC", "ETH"]
BASE_URL = "https://api.glassnode.com/v1/metrics/"

def fetch_metric(metric: str, asset: str) -> pd.DataFrame:
    """Fetch a specific Glassnode metric for a given asset."""
    url = f"{BASE_URL}{METRICS[metric]}"
    params = {"a": asset, "api_key": GLASSNODE_KEY}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["ts"] = pd.to_datetime(df["t"], unit="s")
        df["asset"] = asset
        df["metric"] = metric
        df["value"] = df["v"]
        df["src"] = "glassnode"
        df["meta"] = "{}"
        return df[["ts", "asset", "metric", "value", "src", "meta"]]
    except Exception as e:
        print(f"[❌] Error fetching {metric} for {asset}: {e}")
        return pd.DataFrame()

def save_to_db(df: pd.DataFrame):
    """Insert the DataFrame into the metric_raw table."""
    if df.empty:
        print("[⚠️] No data to save.")
        return
    try:
        with engine.begin() as conn:
            df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
        print(f"[✅] Saved {len(df)} rows to metric_raw.")
    except Exception as e:
        print(f"[❌] Error saving to DB: {e}")

def run_all():
    for metric in METRICS:
        for asset in ASSETS:
            print(f"[⏳] Fetching {metric} for {asset}...")
            df = fetch_metric(metric, asset)
            save_to_db(df)

if __name__ == "__main__":
    run_all()
