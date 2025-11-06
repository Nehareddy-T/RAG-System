import psycopg
from src.core.config import PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

def get_conn():
    return psycopg.connect(
        host=PGHOST, port=PGPORT, dbname=PGDATABASE, user=PGUSER, password=PGPASSWORD
    )
