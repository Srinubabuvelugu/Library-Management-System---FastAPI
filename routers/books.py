
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_roles
from models import User
from schemas import BookCreate, BookResponse, BookUpdate
from services.book_services import get_books, get_book_by_id, create_book, update_book

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/")
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    return get_books(db, page, page_size, search)


@router.get("/{book_id}", response_model=BookResponse)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    book = get_book_by_id(db, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    return book


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("librarian")),
):
    try:
        return create_book(db, book_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.put("/{book_id}", response_model=BookResponse)
def edit_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("librarian")),
):
    try:
        book = update_book(db, book_id, book_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    return book
