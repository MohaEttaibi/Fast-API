from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
import os
# from routers.post import comment_table, post_table
# from routers.user import user_table

os.environ["ENV_STATE"] = "test"

from database import database, user_table  # noqa: E402
from main import app  # noqa: E402

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
    # async with AsyncClient(base_url=client.base_url) as ac:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac

@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details

@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user

@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post("/token", json=confirmed_user)
    return response.json()["access_token"]
    # return response.json().get("token")