from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
import os
# from routers.post import comment_table, post_table

os.environ["ENV_STATE"] = "test"
from database import database #noeqa: E402
from main import app #noeqa: E402

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    # post_table.clear()
    # comment_table.clear()
    await database.connect()
    yield
    await database.disconnect()

@pytest.fixture()
async def async_client() -> AsyncGenerator:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac