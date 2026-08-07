"""FastAPI entrypoint: REST API + Google A2A agent endpoints."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.a2a.server import router as a2a_router
from backend.app.api.routes import router as api_router
from backend.app.core.config import get_settings
from backend.app.core.db import database_available
from backend.app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(a2a_router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("%s starting", settings.app_name)
    logger.info("Local directory storage: %s", settings.data_path)
    logger.info("MCP config: %s", settings.mcp_config_file)
    logger.info("LLM enabled: %s (model=%s)", settings.use_llm, settings.openai_model)
    if not database_available():
        logger.warning(
            "Postgres is not reachable - audit and workflow state will be buffered in memory. "
            "Run db/ddl.sql and check DATABASE_URL in .env."
        )


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs"}
