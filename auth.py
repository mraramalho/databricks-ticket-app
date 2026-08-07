from fastapi import Request
from lakebase import run_query

def get_current_user(request: Request):
    user_email = request.headers.get(
        "X-Forwarded-Email"
    )

    if not user_email:
        raise Exception(
            "User identity not found"
        )

    return user_email


def get_user_role(email: str):
    sql = """
        SELECT role
        FROM app_users
        WHERE user_id = %s
    """

    result = run_query(sql, (email,))

    if not result:
        return "customer"

    return result[0]["role"]