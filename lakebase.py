"""
Lakebase (Databricks-managed Postgres) connection helper.

Connects using a single LAKEBASE_URL (a standard Postgres connection URL,
e.g. postgresql://role:password@host:5432/databricks_postgres?sslmode=require)
pointing at a native Postgres role with a static, non-expiring password.
This keeps setup to a single secret instead of five separate env vars.
"""

import os
from contextlib import contextmanager
import base64
from pathlib import Path

import psycopg2
from databricks.sdk import WorkspaceClient
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

from config import (
    LAKEBASE_SECRET_KEY,
    LAKEBASE_SECRET_SCOPE,
    DEFAULT_ADMIN_SECRET_KEY
)

_w = WorkspaceClient()

_SCOPE = LAKEBASE_SECRET_SCOPE
_KEY = LAKEBASE_SECRET_KEY


def initialize_database():
    schema_path = Path(__file__).parent / "schema_db.sql"
    schema = schema_path.read_text(encoding="utf-8")
    run_write(schema)


def seed_database():
    seed_path = Path(__file__).parent / "seed_data.sql"
    seed = seed_path.read_text(encoding="utf-8")
    run_write(seed)

def _get_default_admin_email():
    """Retrieve the default admin email from secrets."""
    try:
        response = _w.secrets.get_secret(
            scope=_SCOPE,
            key=DEFAULT_ADMIN_SECRET_KEY
        )
        return response.value
    except Exception as e:
        raise RuntimeError(
            f"Failed to retrieve default admin email from secret '{_SCOPE}/{DEFAULT_ADMIN_SECRET_KEY}'. "
            f"Please run setup_secrets.py to configure it. Error: {e}"
        )


def create_default_admin():
    """Create the default admin user from the email stored in secrets."""
    admin_email = _get_default_admin_email()
    sql = """
    INSERT INTO app_users (user_id, role) 
    VALUES (%s, 'admin')
    ON CONFLICT (user_id) DO NOTHING;
    """
    run_write(sql, (admin_email,))

def _lakebase_url() -> str:
    """Fetch and decode the Lakebase connection URL from the Databricks secret scope."""
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    if not secret.value:
        raise Exception(f"LAKEBASE_SECRET_SCOPE={_SCOPE} LAKEBASE_SECRET_KEY={_KEY} not set.")
    
    url = secret.value
    
    # Try to decode from base64 if needed
    # Secret might be stored as base64 or plain text
    if not url.startswith("postgresql://"):
        try:
            # Attempt base64 decode
            decoded = base64.b64decode(url).decode("utf-8")
            # Verify it's a valid PostgreSQL URL after decoding
            if decoded.startswith("postgresql://"):
                url = decoded
            # If decoded doesn't start with postgresql://, use original
        except Exception:
            # If decode fails, assume it's already plain text
            pass
    
    return url

@contextmanager
def get_connection():
    """Yield a raw psycopg2 connection with a RealDictCursor factory."""
    conn = psycopg2.connect(_lakebase_url(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

def get_engine():
    """Return a SQLAlchemy engine for Lakebase."""
    return create_engine(_lakebase_url())

def run_query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Run a read query against Lakebase and return rows as list[dict]."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def run_write(sql: str, params: tuple | dict | None = None) -> int:
    """Run an INSERT/UPDATE/DELETE against Lakebase, return affected row count."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount

def run_write_returning(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Run an INSERT/UPDATE/DELETE with RETURNING clause, return the returned rows as list[dict]."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchall()
