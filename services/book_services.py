from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import Book, Borrow
from schemas import BookCreate, BookResponse, BookUpdate


def get_books(
    db: Session, page: int = 1, page_size: int = 10, search: str | None = None):
    query = db.query(Book)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term)
            )
        )

    total = query.count()

    books = (query.order_by(Book.id).offset((page - 1) * page_size).limit(page_size).all()
    )

    return {
        "items": books,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_book_by_id(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def create_book(db: Session, book_data: BookCreate) -> Book:
    existing_book = (db.query(Book).filter(Book.isbn == book_data.isbn).first())

    if existing_book:
        raise ValueError("A book with this ISBN already exists.")

    book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        total_copies=book_data.total_copies,
        available_copies=book_data.total_copies
    )

    try:
        db.add(book)
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise


def update_book(db: Session,book_id: int,book_data: BookUpdate) -> Book | None:
    book = get_book_by_id(db, book_id)

    if book is None:
        return None

    changes = book_data.model_dump(exclude_unset=True)

    if "isbn" in changes:
        duplicate = (
            db.query(Book)
            .filter(
                Book.isbn == changes["isbn"],
                Book.id != book_id
            )
            .first()
        )

        if duplicate:
            raise ValueError("A book with this ISBN already exists.")

    if "total_copies" in changes:
        borrowed_copies = book.total_copies - book.available_copies

        if changes["total_copies"] < borrowed_copies:
            raise ValueError(
                "Total copies cannot be less than the number of borrowed copies."
            )

        book.available_copies = changes["total_copies"] - borrowed_copies
        book.total_copies = changes["total_copies"]

        changes.pop("total_copies")

    for field, value in changes.items():
        setattr(book, field, value)

    try:
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise


def delete_book(db: Session, book_id: int) -> bool:
    book = get_book_by_id(db, book_id)

    if book is None:
        return False

    active_borrows = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == book_id,
            Borrow.status == "borrowed"
        )
        .first()
    )

    if active_borrows:
        raise ValueError(
            "Cannot delete a book that has active borrow records."
        )

    try:
        db.delete(book)
        db.commit()
        return True

    except Exception:
        db.rollback()
        raise