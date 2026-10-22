from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Date, Float
from sqlalchemy.sql import func # for sql built in functions 
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hash_password = Column(String(255), nullable=False)
    role = Column(Enum("member", "admin", "librarian"), default="member", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    borrows = relationship("Borrow", back_populates="member")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)

    borrows = relationship("Borrow", back_populates="book")


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    borrowed_at = Column(DateTime, nullable=False, server_default=func.now())
    due_date = Column(Date, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="borrowed", nullable=False)

    member = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")