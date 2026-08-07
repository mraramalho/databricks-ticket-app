"""
Lakebase (Databricks-managed Postgres) connection helper.

Connects using a single LAKEBASE_URL (a standard Postgres connection URL,
e.g. postgresql://role:password@host:5432/databricks_postgres?sslmode=require)
pointing at a native Postgres role with a static, non-expiring password.
This keeps setup to a single secret instead of five separate env vars.
"""

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from databricks.sdk import WorkspaceClient
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

from config import (
    LAKEBASE_SECRET_KEY,
    LAKEBASE_SECRET_SCOPE,
    DEFAULT_ADMIN
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

def create_default_admin():
    sql = """
    INSERT INTO app_users (user_id, role) 
    VALUES (%s, 'admin')
    ON CONFLICT (user_id) DO NOTHING;
    """
    run_write(sql, (DEFAULT_ADMIN,))

def _lakebase_url() -> str:
    """Fetch and decode the Lakebase connection URL from the Databricks secret scope."""
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    if secret.value:
        return secret.value
    else:
        raise Exception(f"LAKEBASE_SECRET_SCOPE={_SCOPE} LAKEBASE_SECRET_KEY={_KEY} not set.")

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
