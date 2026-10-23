from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from database import get_db

from dependencies import require_roles
from models import User
from schemas import UserCreate, UserResponse
from services.user_service import create_librarian, get_all_members



router = APIRouter(prefix='/users', tags=['User Management'])

@router.post("/librarians",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def add_librarian(user_data: UserCreate,db: Session = Depends(get_db),current_admin: User = Depends(require_roles("admin"))):
    try:
        librarian = create_librarian(db, user_data)
        return librarian

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.get("/members", response_model=list[UserResponse])
def list_members(db: Session = Depends(get_db),current_admin: User = Depends(require_roles("admin"))):
    return get_all_members(db)