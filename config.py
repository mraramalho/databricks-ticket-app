import os


ENV_MODE = os.getenv(
    "ENV_MODE",
    "development"
)

DEFAULT_ADMIN = os.getenv(
    "DEFAULT_ADMIN"
)

LAKEBASE_SECRET_SCOPE = os.getenv(
    "LAKEBASE_SECRET_SCOPE",
    "database"
)

LAKEBASE_SECRET_KEY = os.getenv(
    "LAKEBASE_SECRET_KEY",
    "lakebase-url"
)