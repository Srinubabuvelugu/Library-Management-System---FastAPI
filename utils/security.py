from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password:str):
    return password_hash.hash(password=password)


def verify_password(plain_password: str,hashed_password: str) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )