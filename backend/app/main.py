from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from . import models
from .routers import auth, cities, readings, alerts

app = FastAPI(title=settings.app_name, version="1.0.0", description="AirWatch air-quality monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"name": "AirWatch API", "status": "online", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(cities.router, prefix=settings.api_prefix)
app.include_router(readings.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
