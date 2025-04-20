# fetcher_service/db.py

import pandas as pd
import psycopg2
from config import get_db_url

def save_ohlcv(df: pd.DataFrame, symbol: str):
    """
    Salva un DataFrame OHLCV giornaliero nel database Neon in public.market_data.
    Ogni valore numpy viene convertito in float() per compatibilità psycopg2.
    """
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    for ts, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO public.market_data
            (timestamp, symbol, interval, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (
                ts, symbol, "daily",
                float(row["open"]), float(row["high"]),
                float(row["low"]),  float(row["close"]),
                float(row["volume"])
            )
        )
    conn.commit()
    cur.close()
    conn.close()

def clear_market_data():
    """
    Elimina **tutti** i record dalla tabella public.market_data.
    Usare con estrema cautela!
    """
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE public.market_data;")
    conn.commit()
    cur.close()
    conn.close()
