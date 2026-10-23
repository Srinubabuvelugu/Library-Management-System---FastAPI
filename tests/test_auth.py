def test_member_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test Member",
            "email": "pytest.member@example.com",
            "password": "TestMember@123"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Member"
    assert data["email"] == "pytest.member@example.com"
    assert data["role"] == "member"


def test_member_login(client):
    client.post(
        "/auth/register",
        json={
            "name": "Login Member",
            "email": "login.member@example.com",
            "password": "LoginMember@123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login.member@example.com",
            "password": "LoginMember@123"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"