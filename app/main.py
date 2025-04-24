import logging

from fastapi import FastAPI

from app.database import init_db
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("Collections created (if not already existing)")


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Notification API"}
