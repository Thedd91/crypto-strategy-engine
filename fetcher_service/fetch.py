# fetcher_service/fetch.py
# Recupera dati OHLCV giornalieri da CoinGecko anche per periodi > 90 giorni

import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_ohlcv(symbol: str, days: int = 30):
    """
    Recupera dati OHLCV giornalieri da CoinGecko.
    - Se days <= 90 usa /market_chart
    - Se days > 90 usa /market_chart/range con parametri from/to
    Restituisce DataFrame con colonne open, high, low, close, volume.
    """
    vs = "usd"
    if days <= 90:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
        params = {"vs_currency": vs, "days": days, "interval": "daily"}
    else:
        to_ts = int(datetime.utcnow().timestamp())
        from_ts = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range"
        params = {"vs_currency": vs, "from": from_ts, "to": to_ts}

    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
        print(f"❌ Errore nella risposta API CoinGecko per {symbol}: {data.get('error', data)}")
        return None

    # Costruisci il DataFrame da prices
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    # Imposta OHLC (CoinGecko fornisce solo prezzo medio giornaliero)
    df["open"]  = df["price"]
    df["high"]  = df["price"]
    df["low"]   = df["price"]
    df["close"] = df["price"]
    df["volume"] = 0.0  # volume non disponibile su endpoint range

    return df[["open", "high", "low", "close", "volume"]]
