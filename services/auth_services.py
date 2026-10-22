from sqlalchemy.orm import Session


from models import User
from schemas import  UserCreate
from utils.security import hash_password, verify_password
from utils.jwt import create_access_token


def register_user(db: Session, user_data: UserCreate) -> User:
    existing_user = (db.query(User).filter(User.email == user_data.email).first())

    if existing_user:
        raise ValueError("Email is already registered.")

    user = User(
        name=user_data.name,
        email=user_data.email,
        hash_password=hash_password(user_data.password),
        role="member"
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> str | None:
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.hash_password):
        return None

    return create_access_token({"sub": str(user.id)})
