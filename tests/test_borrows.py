def test_member_borrow_book(client, db):
    from models import User, Book
    from utils.security import hash_password

    member = User(
        name="Borrow Member",
        email="borrow.pytest@example.com",
        hash_password=hash_password("BorrowMember@123"),
        role="member",
        is_active=True
    )

    book = Book(
        title="Test Borrow Book",
        author="Test Author",
        isbn="9781234567002",
        total_copies=2,
        available_copies=2
    )

    db.add_all([member, book])
    db.commit()
    db.refresh(book)

    login_response = client.post(
        "/auth/login",
        data={
            "username": "borrow.pytest@example.com",
            "password": "BorrowMember@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        f"/borrows/{book.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201

    data = response.json()
    assert data["book_id"] == book.id
    assert data["status"] == "borrowed"




def test_member_cannot_borrow_more_than_three_books(client, db):
    from models import User, Book
    from utils.security import hash_password

    member = User(
        name="Limit Member",
        email="limit.pytest@example.com",
        hash_password=hash_password("LimitMember@123"),
        role="member",
        is_active=True
    )

    books = [
        Book(
            title=f"Limit Book {i}",
            author="Test Author",
            isbn=f"978123456701{i}",
            total_copies=1,
            available_copies=1
        )
        for i in range(1, 5)
    ]

    db.add(member)
    db.add_all(books)
    db.commit()

    login_response = client.post(
        "/auth/login",
        data={
            "username": "limit.pytest@example.com",
            "password": "LimitMember@123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for book in books[:3]:
        response = client.post(
            f"/borrows/{book.id}",
            headers=headers
        )
        assert response.status_code == 201

    fourth_response = client.post(
        f"/borrows/{books[3].id}",
        headers=headers
    )

    assert fourth_response.status_code == 400
    assert fourth_response.json()["detail"] == (
        "You can borrow only 3 books at a time."
    )


def test_member_return_book(client, db):
    from models import User, Book
    from utils.security import hash_password

    member = User(
        name="Return Member",
        email="return.pytest@example.com",
        hash_password=hash_password("ReturnMember@123"),
        role="member",
        is_active=True
    )

    book = Book(
        title="Return Test Book",
        author="Test Author",
        isbn="9781234567020",
        total_copies=2,
        available_copies=2
    )

    db.add_all([member, book])
    db.commit()
    db.refresh(book)

    login_response = client.post(
        "/auth/login",
        data={
            "username": "return.pytest@example.com",
            "password": "ReturnMember@123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    borrow_response = client.post(
        f"/borrows/{book.id}",
        headers=headers
    )

    assert borrow_response.status_code == 201
    borrow_id = borrow_response.json()["id"]

    return_response = client.patch(
        f"/borrows/{borrow_id}/return",
        headers=headers
    )

    assert return_response.status_code == 200
    assert return_response.json()["status"] == "returned"

    db.refresh(book)
    assert book.available_copies == 2



def test_member_borrowing_history(client, db):
    from models import User, Book
    from utils.security import hash_password

    member = User(
        name="History Member",
        email="history.pytest@example.com",
        hash_password=hash_password("HistoryMember@123"),
        role="member",
        is_active=True
    )

    book = Book(
        title="History Test Book",
        author="Test Author",
        isbn="9781234567030",
        total_copies=2,
        available_copies=2
    )

    db.add_all([member, book])
    db.commit()
    db.refresh(book)

    login_response = client.post(
        "/auth/login",
        data={
            "username": "history.pytest@example.com",
            "password": "HistoryMember@123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    borrow_response = client.post(
        f"/borrows/{book.id}",
        headers=headers
    )
    assert borrow_response.status_code == 201

    history_response = client.get(
        "/borrows/my",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) == 1
    assert history[0]["book_id"] == book.id
    assert history[0]["status"] == "borrowed"