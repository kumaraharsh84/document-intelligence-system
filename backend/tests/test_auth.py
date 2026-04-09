import pytest


@pytest.mark.asyncio
async def test_register_login_and_me(client):
    """Verify registration, login, and current-user profile retrieval."""
    register_response = await client.post(
        "/api/users/register",
        json={"email": "auth@example.com", "password": "strongpass"},
    )
    assert register_response.status_code == 200
    register_payload = register_response.json()
    assert register_payload["success"] is True
    assert register_payload["data"]["user"]["email"] == "auth@example.com"

    login_response = await client.post(
        "/api/users/login",
        json={"email": "auth@example.com", "password": "strongpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    me_response = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == "auth@example.com"
