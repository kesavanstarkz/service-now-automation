import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import init_db
from app.api.routes import health, records, ai, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("servicenow_ai_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce Section 5 Startup Guard: AUTH_MODE=dev_bypass must be ENV=dev
    settings.validate_dev_auth_guard()
    logger.info(f"Starting backend: ENV={settings.ENV}, AUTH_MODE={settings.AUTH_MODE}, LLM={settings.LLM_PROVIDER}")

    # Initialize SQLite database tables
    await init_db()
    logger.info("Database tables initialized successfully.")
    
    yield
    logger.info("Shutting down backend.")


app = FastAPI(
    title="ServiceNow AI Assistant API",
    version="1.0.0",
    description="Enterprise AI Assistant Backend for ServiceNow PDI Integration",
    lifespan=lifespan
)

# Enable CORS for browser extension requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Extension origins chrome-extension://*
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(health.router)
app.include_router(records.router)
app.include_router(ai.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "ServiceNow AI Assistant API is running.", "docs": "/docs"}
