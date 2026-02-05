"""
FastAPI application entry point.
Image-Based Product Recognition and Automated Audit Decision System.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import database
from .routes import detection, audit, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    await database.connect()
    print("Application started")
    yield
    # Shutdown
    await database.disconnect()
    print("Application stopped")


app = FastAPI(
    title="Inventory Audit System",
    description="Image-Based Product Recognition and Automated Audit Decision API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(detection.router, prefix="/api/detection", tags=["Detection"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])


@app.get("/")
async def root():
    return {
        "message": "Inventory Audit System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
    )
