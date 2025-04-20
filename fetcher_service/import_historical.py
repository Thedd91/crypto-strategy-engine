# import_historical.py  
print("🔔 import_historical.py avviato.")
import pandas as pd
import os
from db import save_ohlcv, clear_market_data

CSV_DIR = "historical_csv"

def import_all():
    # Svuota la tabella (opzionale)
    clear_market_data()
    # Per ciascun CSV nella cartella
    for fname in os.listdir(CSV_DIR):
        if not fname.lower().endswith(".csv"):
            continue
        symbol = fname.split(".")[0]     # es. 'btc'
        path   = os.path.join(CSV_DIR, fname)
        df = pd.read_csv(path, parse_dates=["snapped_at"])
        df = df.rename(columns={
            "snapped_at": "timestamp",
            "price":      "close",
            "total_volume":"volume"
        })
        df["open"]  = df["close"]
        df["high"]  = df["close"]
        df["low"]   = df["close"]
        df.set_index("timestamp", inplace=True)
        df = df[["open","high","low","close","volume"]]
        save_ohlcv(df, symbol)
    print("✅ Import storico completato per tutti i CSV.")

if __name__ == "__main__":
    import_all()
