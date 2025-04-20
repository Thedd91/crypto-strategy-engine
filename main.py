# fetcher_service/main.py
# Punto di ingresso per recupero dati da CoinGecko e salvataggio su PostgreSQL

from fetch import fetch_ohlcv
from db import save_ohlcv
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Devi specificare il simbolo della coin, es: python main.py pepe")
        sys.exit(1)

    symbol = sys.argv[1]
    print(f"🔍 Recupero dati per: {symbol.upper()}...")

    df = fetch_ohlcv(symbol)
    if df is not None:
        print(f"📊 Dati recuperati: {len(df)} righe")
        save_ohlcv(df, symbol)
        print("✅ Dati salvati nel database.")
    else:
        print("❌ Nessun dato trovato.")
