"""
FastAPI application for Panchanga Service.

This module sets up the FastAPI application with all routes,
middleware, and OpenAPI documentation configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import health_router, panchanga_router, birthdays_router, rules_router, debug_router
from api.routes.slots import router as slots_router

import os

# Application metadata for OpenAPI
APP_TITLE = "Panchanga Service API"
APP_DESCRIPTION = """
## Hindu Calendar (Panchanga) Calculation Service

This API provides comprehensive Panchanga (Hindu calendar) calculations based on 
classical Indian astronomical texts, primarily the **Surya Siddhanta** (ca. AD 1000).

### Features

* **Daily Panchanga**: Calculate all five elements (Tithi, Nakshatra, Yoga, Karana, Vara)
* **Monthly Calendar**: Get Panchanga for an entire month
* **Birthday Finder**: Find future birthdays based on tithi, masa, and paksha
* **Ugadi Dates**: Find upcoming Telugu New Year (Ugadi) dates
* **Multiple Traditions**: Support for Surya, Drik, and Lunar traditions
* **Extensible Rules**: Configurable rules engine for tithi determination

### Traditions

| Tradition | Description |
|-----------|-------------|
| **Surya** | Classical Surya Siddhanta calculations (default) |
| **Drik** | Modern ephemeris-based calculations |
| **Lunar** | Lunar calendar conventions (Amanta/Purnimanta) |

### Languages

The API supports output in:
- Telugu (తెలుగు)
- English
"""

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Panchanga Service starting up...")
    yield
    # Shutdown
    print("Panchanga Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "panchanga",
            "description": "Core Panchanga calculation endpoints"
        },
        {
            "name": "birthdays",
            "description": "Birthday and Ugadi date finder endpoints"
        },
        {
            "name": "rules",
            "description": "Rules and traditions management endpoints"
        },
        {
            "name": "slots",
            "description": "Slot computation and time validation for ritual allocation"
        },
        {
            "name": "debug",
            "description": "Debug endpoints for verifying calculation accuracy (development only)"
        }
    ]
)

# Configure CORS
ALLOWED_ORIGINS = [
    "https://panchang.sathkaal.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(panchanga_router, prefix="/api/v1/panchanga", tags=["panchanga"])
app.include_router(birthdays_router, prefix="/api/v1/panchanga/birthdays", tags=["birthdays"])
app.include_router(rules_router, prefix="/api/v1/rules", tags=["rules"])
app.include_router(slots_router, prefix="/api/v1/panchanga", tags=["slots"])

if os.getenv("ENABLE_DEBUG_ROUTES", "false").lower() == "true":
    print("Debug routes enabled")
    app.include_router(debug_router, prefix="/api/v1/panchanga", tags=["debug"])
else:
    print("Debug routes disabled")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "service": "Panchanga Service",
        "version": APP_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
