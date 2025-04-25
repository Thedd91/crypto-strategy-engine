import os
from dotenv import load_dotenv

# Carica variabili da .env se presente
load_dotenv()

def get_db_url():
    return "postgresql://postgres.eceyiyehmyoqsqgemywn:Ibrahimovic91@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

