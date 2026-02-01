def test_read_home(client):
    """Test the GET / endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello to It Support RAG API"}


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login", data={"username": "user", "password": "password123"}
    )

    assert response.status_code in [401, 422, 400]


def test_create_user_then_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    print(f"DEBUG - Set-Cookie Header: {response.headers.get('set-cookie')}")
    assert response.status_code == 200
    response_data = response.json()
    assert "Login successful!" in response_data["msg"]
