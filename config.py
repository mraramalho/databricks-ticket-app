import os


ENV_MODE = os.getenv(
    "ENV_MODE",
    "development"
)

LAKEBASE_SECRET_SCOPE = os.getenv(
    "LAKEBASE_SECRET_SCOPE",
    "database"
)

LAKEBASE_SECRET_KEY = os.getenv(
    "LAKEBASE_SECRET_KEY",
    "lakebase-url"
)

DEFAULT_ADMIN_SECRET_KEY = os.getenv(
    "DEFAULT_ADMIN_SECRET_KEY",
    "default-admin-email"
)