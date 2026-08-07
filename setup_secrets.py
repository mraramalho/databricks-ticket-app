from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

from config import (
    LAKEBASE_SECRET_SCOPE,
    LAKEBASE_SECRET_KEY,
)


w = WorkspaceClient()

try:
    w.secrets.create_scope(
        scope=LAKEBASE_SECRET_SCOPE
    )
    print(
        f"Secret scope '{LAKEBASE_SECRET_SCOPE}' created."
    )

except Exception as e:
    if "already exists" in str(e).lower():
        print(
            f"Secret scope '{LAKEBASE_SECRET_SCOPE}' already exists."
        )
    else:
        raise


lakebase_url = getpass.getpass(
    "Paste your Lakebase URL: "
)


w.secrets.put_secret(
    scope=LAKEBASE_SECRET_SCOPE,
    key=LAKEBASE_SECRET_KEY,
    string_value=lakebase_url,
)


w.secrets.put_acl(
    scope=LAKEBASE_SECRET_SCOPE,
    principal="users",
    permission=workspace.AclPermission.READ,
)


print("Secret configured successfully.")