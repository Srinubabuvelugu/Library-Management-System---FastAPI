from sqlalchemy.orm import Session


from models import User
from schemas import UserCreate
from utils.security import hash_password


def create_librarian(db: Session, user_data: UserCreate) -> User:
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email is already registered.")

    librarian = User(
        name=user_data.name,
        email=user_data.email,
        hash_password=hash_password(user_data.password),
        role="librarian",
        is_active=True
    )

    try:
        db.add(librarian)
        db.commit()
        db.refresh(librarian)
        return librarian
    except Exception:
        db.rollback()
        raise


def get_all_members(db: Session):
    return (
        db.query(User)
        .filter(User.role == "member")
        .order_by(User.id.desc())
        .all()
    )