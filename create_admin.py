from getpass import getpass

from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import User
from utils.security import hash_password



def create_admin():
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User)
            .filter(User.role == "admin")
            .first()
        )

        if existing_admin:
            print("An admin account already exists.")
            return

        name = input("Enter admin name: ").strip()
        email = input("Enter admin email: ").strip().lower()
        password = getpass("Enter admin password: ")
        confirm_password = getpass("Confirm admin password: ")

        if not name or not email:
            print("Name and email are required.")
            return

        if len(password) < 6:
            print("Admin password must contain at least 12 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        admin = User(
            name=name,
            email=email,
            hash_password=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully.")

    except IntegrityError:
        db.rollback()
        print("This email is already registered.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
