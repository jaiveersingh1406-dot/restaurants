import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-9f2c1a")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_or_upgrade_password(plain_password: str, stored_hash: str, upgrade_callback=None) -> bool:
    """Verify password; supports legacy plaintext rows by upgrading them to bcrypt."""
    if stored_hash and stored_hash.startswith("$2"):
        return pwd_context.verify(plain_password, stored_hash)

    if plain_password == stored_hash:
        if upgrade_callback is not None:
            upgrade_callback(hash_password(plain_password))
        return True

    return False


def create_access_token(email: str, role: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
