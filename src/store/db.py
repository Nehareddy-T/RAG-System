import psycopg
from psycopg import OperationalError
from src.core.config import PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
from src.core.logging import get_logger

# Initialize logger for the database module
logger = get_logger("db")

def get_conn():
    """
    Establish and return a database connection.
    Handles connection errors gracefully with clear logs and user guidance.
    """
    try:
        conn = psycopg.connect(
            host=PGHOST,
            port=PGPORT,
            dbname=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
        )
        return conn

    except OperationalError as e:
        # Log a clear, production-level error message
        logger.error(
            f"❌ Database connection failed: Unable to reach Postgres at {PGHOST}:{PGPORT}. "
            "Ensure Docker is running and the pgvector container is active."
        )

        # Exit gracefully with actionable feedback for the developer
        raise SystemExit(
            "\n[ERROR] Could not connect to the Postgres database.\n"
            f"Reason: {e}\n\n"
            "👉 To fix this, make sure your database container is running:\n"
            "   docker compose up -d\n"
        )
