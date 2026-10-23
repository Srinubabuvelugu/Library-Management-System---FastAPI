from datetime import date, timedelta
from sqlalchemy.orm import Session

from models import Book, Borrow, User
from datetime import date, datetime
from schemas import BorrowStatus

from sqlalchemy import func


MAX_ACTIVE_BORROWS = 3
BORROW_DAYS = 14
FINE_PER_DAY = 5


def borrow_book(db: Session, member_id: int, book_id: int):
    # Check whether the book exists
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        raise ValueError("Book not found.")

    # Check available copies
    if book.available_copies <= 0:
        raise ValueError("No copies of this book are available.")

    # Count currently active borrows
    active_borrows = (
        db.query(Borrow)
        .filter(
            Borrow.member_id == member_id,
            Borrow.status == "borrowed"
        )
        .count()
    )

    if active_borrows >= MAX_ACTIVE_BORROWS:
        raise ValueError("You can borrow only 3 books at a time.")

    # Prevent borrowing the same book twice while it is active
    existing_borrow = (
        db.query(Borrow)
        .filter(
            Borrow.member_id == member_id,
            Borrow.book_id == book_id,
            Borrow.status == "borrowed"
        )
        .first()
    )

    if existing_borrow:
        raise ValueError("You have already borrowed this book.")

    # Create borrowing record
    borrow = Borrow(
        member_id=member_id,
        book_id=book_id,
        due_date=date.today() + timedelta(days=BORROW_DAYS),
        status="borrowed"
    )

    try:
        book.available_copies -= 1

        db.add(borrow)
        db.commit()
        db.refresh(borrow)

        return borrow

    except Exception:
        db.rollback()
        raise


def return_book(db: Session, member_id: int, borrow_id: int):
    borrow = (
        db.query(Borrow)
        .filter(
            Borrow.id == borrow_id,
            Borrow.member_id == member_id,
            Borrow.status == "borrowed"
        )
        .first()
    )

    if borrow is None:
        raise ValueError("Active borrow record not found.")

    try:
        today = date.today()
        return_time = datetime.now()

        overdue_days = (today - borrow.due_date).days

        if overdue_days > 0:
            borrow.fine_amount = overdue_days * FINE_PER_DAY
        else:
            borrow.fine_amount = 0

        borrow.returned_at = return_time
        borrow.status = "returned"

        borrow.book.available_copies += 1

        db.commit()
        db.refresh(borrow)

        return borrow

    except Exception:
        db.rollback()
        raise


def get_borrowing_history(db: Session, member_id: int, status:str=None):
    query = db.query(Borrow).filter(Borrow.member_id == member_id)

    if status:
        query = query.filter(Borrow.status == status)

    return query.order_by(Borrow.borrowed_at.desc()).all()



def get_all_borrow_records(db: Session,status: BorrowStatus | None = None):
    query = db.query(Borrow)

    if status is not None:
        query = query.filter(Borrow.status == status.value)

    return query.order_by(Borrow.borrowed_at.desc()).all()


def get_overdue_borrows(db: Session):
    return (
        db.query(Borrow)
        .filter(Borrow.status == "borrowed",Borrow.due_date < date.today())
        .order_by(Borrow.due_date.asc())
        .all()
    )


def get_library_report(db: Session):
    total_books = db.query(Book).count()

    total_members = (
        db.query(User)
        .filter(User.role == "member")
        .count()
    )

    active_borrows = (
        db.query(Borrow)
        .filter(Borrow.status == "borrowed")
        .count()
    )

    returned_books = (
        db.query(Borrow)
        .filter(Borrow.status == "returned")
        .count()
    )

    overdue_books = (
        db.query(Borrow)
        .filter(
            Borrow.status == "borrowed",
            Borrow.due_date < date.today()
        )
        .count()
    )

    total_fines = (
        db.query(func.sum(Borrow.fine_amount))
        .scalar()
        or 0
    )

    return {
        "total_books": total_books,
        "total_members": total_members,
        "active_borrows": active_borrows,
        "returned_books": returned_books,
        "overdue_books": overdue_books,
        "total_fines": float(total_fines)
    }