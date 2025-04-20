# fetcher_service/fetch.py
# Recupera dati OHLCV da CoinGecko

import requests
import pandas as pd
from datetime import datetime

def get_coin_id(name: str):
    try:
        coin_list_url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(coin_list_url)
        coins = response.json()

        # Cerca per symbol esatto
        matches = [coin for coin in coins if coin['symbol'] == name.lower()]
        if matches:
            return matches[0]['id']

        # Altrimenti prova con id diretto
        for coin in coins:
            if coin['id'] == name.lower():
                return coin['id']

        print("❌ Coin non trovata nella lista CoinGecko")
        return None
    except Exception as e:
        print(f"❌ Errore nel recupero ID CoinGecko: {e}")
        return None

def fetch_ohlcv(symbol: str, days: int = 30):
    try:
        coin_id = get_coin_id(symbol)
        if coin_id is None:
            return None

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "hourly"}
        response = requests.get(url, params=params)
        data = response.json()

        print("DEBUG - Risposta API:", data if len(str(data)) < 300 else str(data)[:300] + "...")

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
        df["volume"] = 0.0
        return df[["open", "high", "low", "close", "volume"]]

    except Exception as e:
        print(f"❌ Errore fetch dati CoinGecko: {e}")
        return None
