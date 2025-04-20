# init_db.py (da mettere nella stessa cartella: fetcher_service)
import psycopg2
from config import get_db_url

def create_table():
    try:
        conn = psycopg2.connect(get_db_url())
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.market_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION,
                UNIQUE(timestamp, symbol, interval)
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabella 'market_data' creata correttamente.")
    except Exception as e:
        print(f"❌ Errore nella creazione della tabella: {e}")

if __name__ == "__main__":
    create_table()
