
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=2, max_length=150)
    isbn: str = Field(..., min_length=10, max_length=20)
    total_copies: int = Field(default=1, ge=1, le=1000)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int

    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=2, max_length=150)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=20)
    total_copies: Optional[int] = Field(default=None, ge=1, le=1000)


class BorrowResponse(BaseModel):
    id: int
    member_id: int
    book_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: Optional[datetime] = None
    fine_amount: float
    status: str

    model_config = ConfigDict(from_attributes=True)
