import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from lakebase import initialize_database, seed_database, create_default_admin, run_query
from config import ENV_MODE
from tickets import router as tickets_router
from auth import get_current_user, get_user_role

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    initialize_database()
    if ENV_MODE.lower() == 'development':
        print("Running in development mode")
        print("Loading dummy data")
        seed_database()
    create_default_admin()

app.include_router(
    tickets_router
)

@app.get("/")
def root(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@app.get("/api/auth/me")
def get_current_user_info(request: Request):
    """
    Returns the current authenticated user's email and role.
    """
    try:
        email = get_current_user(request)
        role = get_user_role(email)
        
        return {
            "email": email,
            "role": role
        }
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": str(e)
            }
        )


@app.get("/health")
@app.get("/api/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Verifies both application and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "service": "ticket-system",
        "components": {
            "application": "up",
            "database": "unknown"
        }
    }
    
    # Test database connection
    try:
        result = run_query("SELECT 1 as health_check")
        if result and result[0].get("health_check") == 1:
            health_status["components"]["database"] = "up"
        else:
            health_status["components"]["database"] = "down"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["database"] = "down"
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    # Return 503 if unhealthy, 200 if healthy
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(content=health_status, status_code=status_code)
