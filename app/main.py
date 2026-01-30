from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.api.v1.api import api_router
from app.modules.auth.routers.router import router as auth_router
from app.shared.exceptions.exceptions import BaseAppException
from app.shared.responses.responses import ErrorResponse
from app.core.database.db_connect.database import engine
from app.core.middleware.auth_middleware import auth_middleware


# ------------------- LIFESPAN -------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print(" Database connected")
    except Exception as e:
        print(" Database connection failed")
        raise e

    yield  # <-- Application runs here

    # SHUTDOWN
    await engine.dispose()
    print(" Database connection closed")


# ------------------- APP -------------------

app = FastAPI(
    title="FastAPI + Keycloak",
    lifespan=lifespan
)

# Add authentication middleware
app.middleware("http")(auth_middleware)


# ------------------- EXCEPTION HANDLERS -------------------

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.detail
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"=" * 80)
    print(f"❌ UNHANDLED EXCEPTION on {request.method} {request.url}")
    print(f"=" * 80)
    traceback.print_exc()
    print(f"=" * 80)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred"
        ).dict()
    )


# ------------------- ROUTERS -------------------

app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
