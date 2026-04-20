"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from utils.config import get_settings
from utils.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)
    settings = get_settings()
    logger.info("Backend avviato (log level=%s)", settings.LOG_LEVEL)
    yield
    logger.info("Backend in chiusura")


app = FastAPI(title="MDK Frontline Backend", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
