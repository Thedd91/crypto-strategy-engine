# fetcher_service/fetch.py
# Recupera dati OHLCV giornalieri da CoinGecko su periodi >365 giorni spezzettando il range

import requests
import pandas as pd
from datetime import datetime, timedelta

MAX_DAYS = 365  # limite Public API

def fetch_ohlcv(symbol: str, days: int = 30):
    """
    Recupera dati OHLCV giornalieri da CoinGecko:
    - Se days <= 365 usa /market_chart
    - Se days  > 365 spezza in finestre di 365 gg con /market_chart/range
    Restituisce DataFrame con colonne open, high, low, close, volume.
    """

    def fetch_range(from_ts, to_ts):
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range"
        params = {"vs_currency": "usd", "from": from_ts, "to": to_ts}
        r = requests.get(url, params=params)
        d = r.json()
        if "prices" not in d:
            raise ValueError(d.get("error") or d)
        df0 = pd.DataFrame(d["prices"], columns=["timestamp", "price"])
        df0["timestamp"] = pd.to_datetime(df0["timestamp"], unit="ms")
        df0.set_index("timestamp", inplace=True)
        df0["open"]  = df0["price"]
        df0["high"]  = df0["price"]
        df0["low"]   = df0["price"]
        df0["close"] = df0["price"]
        df0["volume"] = 0.0
        return df0[["open","high","low","close","volume"]]

    now = datetime.utcnow()
    if days <= MAX_DAYS:
        # chiamata singola
        from_ts = int((now - timedelta(days=days)).timestamp())
        to_ts   = int(now.timestamp())
        return fetch_range(from_ts, to_ts)
    else:
        # spezza in finestre di MAX_DAYS
        frames = []
        chunks = (days // MAX_DAYS) + 1
        for i in range(chunks):
            end   = now - timedelta(days=i * MAX_DAYS)
            start = end - timedelta(days=MAX_DAYS)
            # ultimo chunk potrebbe eccedere in partenza
            if (now - start).days > days:
                start = now - timedelta(days=days)
            df_chunk = fetch_range(int(start.timestamp()), int(end.timestamp()))
            frames.append(df_chunk)
        # concat, ordina, rimuovi duplicati
        df = pd.concat(frames)
        df = df[~df.index.duplicated(keep="first")]
        df.sort_index(inplace=True)
        return df
