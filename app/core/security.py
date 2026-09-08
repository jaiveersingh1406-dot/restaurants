import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-9f2c1a")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BCRYPT_MAX_BYTES = 72


def _truncate_password(password: str) -> str:
    """Truncate a password to bcrypt's 72-byte limit without splitting a multibyte char."""
    data = password.encode("utf-8")
    if len(data) <= BCRYPT_MAX_BYTES:
        return password
    return data[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    return pwd_context.hash(_truncate_password(password))


def verify_or_upgrade_password(plain_password: str, stored_hash: str, upgrade_callback=None) -> bool:
    """Verify password; supports legacy plaintext rows by upgrading them to bcrypt."""
    plain_password = _truncate_password(plain_password)
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
