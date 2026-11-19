from pwdlib import PasswordHash
from config import settings
from datetime import datetime, timedelta, timezone
import jwt

password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"

def hash_password_func(password: str) -> str:
    return password_hash.hash(password)

def verify_password_func(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=ALGORITHM
    )

    return token

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[ALGORITHM],
        options={"require": ["sub", "exp"]}
    )

    return payload