"""
Airline Fuel Management System — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from application.config import settings

# ── Import all models so Alembic/SQLAlchemy can discover them ─────────────────
from application.src.models import (  # noqa: F401
    role_model,
    menu_model,
    role_menu_permission_model,
    audit_log_model,
    user_model,
    airline_model,
    vendor_model,
    fuel_price_model,
    transaction_model,
)

# ── Routers ───────────────────────────────────────────────────────────────────
from application.controllers.api.auth_controller import router as auth_router
from application.controllers.api.airline_controller import router as airline_router
from application.controllers.api.vendor_controller import router as vendor_router
from application.controllers.api.fuel_price_controller import router as fuel_price_router
from application.controllers.api.transaction_controller import router as transaction_router
from application.controllers.api.report_controller import router as report_router
from application.controllers.api.notification_controller import router as notification_router
from application.controllers.api.user_controller import router as user_router
from application.controllers.api.role_controller import router as role_router
from application.controllers.api.menu_controller import router as menu_router
from application.controllers.api.permission_controller import router as permission_router
from application.core.redis import init_redis_pool, close_redis_pool

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown hooks) ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀  %s is starting up …", settings.PROJECT_NAME)
    await init_redis_pool()
    yield
    await close_redis_pool()
    logger.info("🛑  %s is shutting down.", settings.PROJECT_NAME)


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## Airline Fuel Management System API

A production-ready backend for managing airline fuel operations.

### Key Features
- 🔐 JWT Authentication
- ✈️  Airline Management
- ⛽  Fuel Vendor Management
- 💰  Fuel Price Tracking (with full history)
- 📋  Fuel Transaction Recording with Auto Invoice Generation
- 📊  Reports & Dashboard Analytics

### Business Rules
1. Each vendor can have multiple fuel price records (tracked historically).
2. The **latest** fuel price is automatically selected when creating a transaction.
3. Invoice numbers follow the format: `INV-YYYYMMDD-XXXX`.
4. `total_amount = fuel_quantity × fuel_price`
5. If no fuel price exists for a vendor, transaction creation is **blocked**.
""",
    contact={
        "name": "Fuel System Team",
        "email": "admin@fuelsystem.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(airline_router)
app.include_router(vendor_router)
app.include_router(fuel_price_router)
app.include_router(transaction_router)
app.include_router(report_router)
app.include_router(notification_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(menu_router)
app.include_router(permission_router)


# ── Static Files (logos, etc.) ────────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="API health check")
async def health():
    """Returns 200 OK when the service is running."""
    from application.core.redis import redis_health
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "redis": await redis_health(),
    }


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "redoc": "/redoc",
    }
