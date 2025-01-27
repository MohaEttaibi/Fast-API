from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.post import router as post_router
from database import database
from logging_config import configure_logging

# import logging
# logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # logger.info("App Running")
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(post_router)