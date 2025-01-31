from httpx import AsyncClient
import pytest

async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password":password}
    )

@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@gmail.com", "123456")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]