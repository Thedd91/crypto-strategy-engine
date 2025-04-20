# backfill.py — Script per costruire lo storico delle coin in base al Tier (eseguibile anche da Streamlit o CLI)
import pandas as pd
from fetch import fetch_ohlcv
from db import save_ohlcv
from datetime import datetime
import os

# 🧠 Mappatura simbolo semplificato → ID CoinGecko
COIN_ID_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "xrp": "ripple",
    "ltc": "litecoin",
    "ada": "cardano",
    "sol": "solana",
    "dot": "polkadot",
    "avax": "avalanche-2",
    "matic": "polygon",
    "link": "chainlink",
    "atom": "cosmos",
    "doge": "dogecoin",
    "shib": "shiba-inu",
    "pepe": "pepe",
    "wif": "dogwifcoin",
    "bonk": "bonk",
    "floki": "floki"
}

# Log file
LOG_FILE = "backfill_log.csv"

# Tier e profondità storica (in giorni)
TIERS = {
    "tier1": {
        "coins": ["btc", "eth", "bnb", "xrp", "ltc"],
        "days": 365 * 10
    },
    "tier2": {
        "coins": ["ada", "sol", "dot", "avax", "matic", "link", "atom"],
        "days": 365 * 5
    },
    "tier3": {
        "coins": ["doge", "shib", "pepe", "wif", "bonk", "floki"],
        "days": 365 * 2
    }
}

def get_last_run_date():
    if os.path.exists(LOG_FILE):
        return datetime.fromtimestamp(os.path.getmtime(LOG_FILE)).strftime("%Y-%m-%d %H:%M")
    return None

def run_backfill():
    logs = []
    for tier, data in TIERS.items():
        print(f"📚 Tier: {tier.upper()} (Days: {data['days']})")
        for symbol in data["coins"]:
            coin_id = COIN_ID_MAP.get(symbol, symbol)
            try:
                print(f"  ⏳ Fetching {coin_id}...")
                df = fetch_ohlcv(coin_id, data["days"])
                if df is not None and not df.empty:
                    print(f"  💾 Salvando {len(df)} righe per {symbol}...")
                    save_ohlcv(df, symbol)
                    print("  ✅ Completato\n")
                    logs.append({"symbol": symbol, "status": "OK", "rows": len(df)})
                else:
                    print("  ⚠️ Nessun dato trovato\n")
                    logs.append({"symbol": symbol, "status": "NODATA", "rows": 0})
            except Exception as e:
                print(f"  ❌ Errore con {symbol}: {e}\n")
                logs.append({"symbol": symbol, "status": f"ERROR: {e}", "rows": 0})
    pd.DataFrame(logs).to_csv(LOG_FILE, index=False)
    print(f"✅ Backfill completato! Log salvato in {LOG_FILE}")

# Esecuzione solo se lanciato da terminale (non quando importato da Streamlit)
if __name__ == "__main__":
    last_run = get_last_run_date()
    if last_run:
        print(f"⚠️ Attenzione: Il backfill è stato eseguito l'ultima volta il {last_run}")
        confirm = input("👉 Sei sicuro di volerlo rieseguire? (s/N): ").lower()
        if confirm != "s":
            print("⏹️ Backfill annullato.")
            exit()
    print("🚀 Inizio backfill storico...\n")
    run_backfill()
