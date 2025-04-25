# file: data_services/macro_service/macro_fetcher.py

import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_CONN = os.getenv("SUPABASE_CONN")
assert SUPABASE_CONN, "Missing SUPABASE_CONN"

engine = create_engine(SUPABASE_CONN)

# Fear & Greed API Endpoint
FNG_API = "https://api.alternative.me/fng/"

def fetch_fng() -> pd.DataFrame:
    try:
        res = requests.get(FNG_API, timeout=10)
        res.raise_for_status()
        data = res.json().get("data", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["ts"] = pd.to_datetime(df["timestamp"], unit="s")
        df["asset"] = "CRYPTO"
        df["metric"] = "fear_greed_index"
        df["value"] = pd.to_numeric(df["value"])
        df["src"] = "alternative.me"
        df["meta"] = df[["value_classification"]].to_json(orient="records")
        return df[["ts", "asset", "metric", "value", "src", "meta"]]
    except Exception as e:
        print(f"[❌] Error fetching Fear & Greed Index: {e}")
        return pd.DataFrame()

def save_to_db(df: pd.DataFrame):
    if df.empty:
        print("[⚠️] No data to save.")
        return
    try:
        with engine.begin() as conn:
            df.to_sql("metric_raw", con=conn, if_exists="append", index=False, method="multi")
        print(f"[✅] Saved {len(df)} rows to metric_raw.")
    except Exception as e:
        print(f"[❌] Error saving to DB: {e}")

if __name__ == "__main__":
    print("[⏳] Fetching Fear & Greed Index...")
    df = fetch_fng()
    save_to_db(df)
