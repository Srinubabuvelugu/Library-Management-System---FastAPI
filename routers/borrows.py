from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from dependencies import get_current_user, require_roles
from models import User
from schemas import BorrowResponse, BorrowStatus
from services.borrow_service import borrow_book, return_book, get_borrowing_history, get_all_borrow_records, get_overdue_borrows, get_library_report

router = APIRouter(prefix="/borrows", tags=["Borrowing"])


@router.post("/{book_id}",response_model=BorrowResponse,status_code=status.HTTP_201_CREATED)
def borrow_book_api(book_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    # Only members can borrow books
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can borrow books."
        )

    try:
        return borrow_book(db, current_user.id, book_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )



@router.patch("/{borrow_id}/return", response_model=BorrowResponse)
def return_book_api(borrow_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can return books."
        )

    try:
        return return_book(db, current_user.id, borrow_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.get('/my', response_model=List[BorrowResponse])
def borrowing_history(db: Session = Depends(get_db),current_user: User = Depends(get_current_user), borrow_status :BorrowStatus | None=Query(default=None, alias="Status")):
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can view borrowing history."
        )

    return get_borrowing_history(db, current_user.id, borrow_status)



@router.get("", response_model=list[BorrowResponse])
def get_all_borrows(
    borrow_status: BorrowStatus | None = Query(default=None,alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("librarian", "admin"))
):
    return get_all_borrow_records(db, borrow_status)


@router.get("/overdue", response_model=list[BorrowResponse])
def overdue_borrows(db: Session = Depends(get_db),current_user: User = Depends(require_roles("librarian", "admin"))):
    return get_overdue_borrows(db)


@router.get("/reports")
def library_reports(db: Session = Depends(get_db),current_user: User = Depends(require_roles("admin"))):
    return get_library_report(db)