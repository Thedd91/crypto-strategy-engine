# fetcher_service/fetch.py
# Recupera dati OHLCV da CoinGecko

import requests
import pandas as pd
from datetime import datetime

def fetch_ohlcv(symbol: str, days: int = 30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "hourly"}
        response = requests.get(url, params=params)
        data = response.json()

        if "prices" not in data:
            print("❌ Errore nella risposta API CoinGecko")
            return None

        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")
        df["open"] = df["price"]
        df["high"] = df["price"]
        df["low"] = df["price"]
        df["close"] = df["price"]
        df["volume"] = 0.0  # CoinGecko non fornisce volume hourly qui
        return df[["open", "high", "low", "close", "volume"]]

    except Exception as e:
        print(f"❌ Errore fetch dati CoinGecko: {e}")
        return None
