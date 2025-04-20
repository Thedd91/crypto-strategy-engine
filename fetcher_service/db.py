# db.py (fix finale: conversione esplicita valori per evitare np.float64 e schema public)
import psycopg2
from config import get_db_url
from datetime import datetime

def save_ohlcv(df, symbol: str):
    try:
        conn = psycopg2.connect(get_db_url())
        cursor = conn.cursor()

        for timestamp, row in df.iterrows():
            ts = timestamp if isinstance(timestamp, datetime) else pd.to_datetime(timestamp)
            open_ = float(row["open"])
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            volume = float(row["volume"])

            cursor.execute("""
                INSERT INTO public.market_data (timestamp, symbol, interval, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, symbol, interval) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume;
            """, (
                ts,
                symbol,
                "1d",
                open_, high, low, close, volume
            ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise e


def clear_market_data():
    """
    Elimina **tutti** i record** dalla tabella public.market_data.
    Usare con estrema cautela!
    """
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE public.market_data;")
    conn.commit()
    cur.close()
    conn.close()
