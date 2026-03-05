from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

_WEAK_KEY_MARKERS = ["dev-secret-key", "change-in-production", "rolefit-super-secret"]
if any(marker in SECRET_KEY for marker in _WEAK_KEY_MARKERS) or len(SECRET_KEY) < 32:
    import logging as _logging
    _logger = _logging.getLogger("rolefit.security")
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError(
            "FATAL: Weak SECRET_KEY detected in production. "
            "Generate a strong key: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    else:
        _logger.warning("Using weak SECRET_KEY — change this before deploying.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def _get_fernet() -> Fernet:
    enc_key_source = os.getenv("ENCRYPTION_KEY", SECRET_KEY)
    key = base64.urlsafe_b64encode(hashlib.sha256(enc_key_source.encode("utf-8")).digest())
    return Fernet(key)


def encrypt_api_key(api_key: str) -> Optional[str]:
    if not api_key:
        return None
    f = _get_fernet()
    return f.encrypt(api_key.encode("utf-8")).decode("utf-8")


def decrypt_api_key(encrypted_key: str) -> Optional[str]:
    if not encrypted_key:
        return None
    f = _get_fernet()
    try:
        return f.decrypt(encrypted_key.encode("utf-8")).decode("utf-8")
    except Exception:
        return None
