def test_librarian_create_book(client, db):
    from models import User
    from utils.security import hash_password

    librarian = User(
        name="Test Librarian",
        email="librarian.pytest@example.com",
        hash_password=hash_password("Librarian@123"),
        role="librarian",
        is_active=True
    )

    db.add(librarian)
    db.commit()
    db.refresh(librarian)

    login_response = client.post(
        "/auth/login",
        data={
            "username": "librarian.pytest@example.com",
            "password": "Librarian@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Pytest Book",
            "author": "Test Author",
            "isbn": "9781234567001",
            "total_copies": 5
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Pytest Book"
    assert data["total_copies"] == 5
    assert data["available_copies"] == 5



def test_member_cannot_create_book(client, db):
    from models import User
    from utils.security import hash_password

    member = User(
        name="Unauthorized Member",
        email="unauthorized.pytest@example.com",
        hash_password=hash_password("Member@123"),
        role="member",
        is_active=True
    )

    db.add(member)
    db.commit()

    login_response = client.post(
        "/auth/login",
        data={
            "username": "unauthorized.pytest@example.com",
            "password": "Member@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Unauthorized Book",
            "author": "Test Author",
            "isbn": "9781234567040",
            "total_copies": 2
        }
    )

    assert response.status_code == 403

def test_member_cannot_delete_book(client, db):
    from models import User, Book
    from utils.security import hash_password

    member = User(
        name="Test Member",
        email="delete.member@example.com",
        hash_password=hash_password("Member@123"),
        role="member",
        is_active=True
    )

    book = Book(
        title="Test Delete Book",
        author="Test Author",
        isbn="9781234567041",
        total_copies=2,
        available_copies=2
    )

    db.add_all([member, book])
    db.commit()
    db.refresh(book)

    login_response = client.post(
        "/auth/login",
        data={
            "username": "delete.member@example.com",
            "password": "Member@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.delete(
        f"/books/{book.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403