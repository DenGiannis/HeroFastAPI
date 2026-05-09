from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import asynccontextmanager
import time
import uuid

from routers import heroes, missions, auth
from db import create_db_and_tables
from config import get_settings


# Lifespan function to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: cleanup."""
    create_db_and_tables()
    print("Database ready [OK]")
    yield
    print("Shutting down...")

settings = get_settings()

# FastAPI app instance
app = FastAPI(
    title="Heroes FastAPI",
    description="A simple API to manage heroes and their missions.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom timing middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(TimingMiddleware)

# Routers
app.include_router(heroes.router)
app.include_router(missions.router) 
app.include_router(auth.router)

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Welcome message."""
    return {"message": "Welcome to the Heroes API!"}