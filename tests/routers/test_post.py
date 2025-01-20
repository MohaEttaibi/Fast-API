from httpx import AsyncClient
import pytest

async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/post", json={"body": body})
    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test Post", async_client)

