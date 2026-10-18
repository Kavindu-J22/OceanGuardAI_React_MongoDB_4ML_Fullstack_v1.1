from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import logger
from app.db.connection import db_manager, get_database
from app.db.indexes import create_indexes
from app.api.v1 import auth, vessels, trips, ml, observations, rescue, models, data, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing OceanGuard AI Backend Services...")
    db = get_database()
    create_indexes(db)
    
    # Auto-seed if database is brand new / mock
    if db.users.count_documents({}) == 0:
        logger.info("Empty database detected. Running automated bootstrap seeding...")
        from scripts.seed_db import seed
        seed()
    logger.info("OceanGuard AI Startup Initialization Completed.")
    yield
    logger.info("Shutting down OceanGuard AI Backend Services...")
    db_manager.close()

app = FastAPI(
    title="OceanGuard AI — REST API",
    description="Advanced AI-Driven Offline-First Safety, Fishing Intelligence, Fuel Prediction and Market Decision System for Artisanal Fishing Vessels.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. System administrators have been notified."}
    )

# Include Routers
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(vessels.router, prefix=settings.API_V1_STR)
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(ml.router, prefix=settings.API_V1_STR)
app.include_router(observations.router, prefix=settings.API_V1_STR)
app.include_router(rescue.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(data.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": "OceanGuard AI",
        "description": "Artisanal Fishing Safety & Multi-Component Intelligence System",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health/ready"
    }
