import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .database import get_db
from . import models

# ---------- Настройки ----------

SECRET_KEY = 'CHANGE_ME_IN_PRODUCTION_use_env_variable'
ALGORITHM = 'HS256'
TOKEN_LIFETIME_HOURS = 48

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# ---------- Пароли ----------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


# ---------- Токены ----------

def create_access_token(user_id: int, username: str, group: str) -> tuple[str, int]:
    """Создаёт JWT. Возвращает (токен, срок жизни в секундах)."""
    expires_delta = timedelta(hours=TOKEN_LIFETIME_HOURS)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        'sub': str(user_id),
        'username': username,
        'group': group,
        'exp': expire,
        'iat': datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expires_delta.total_seconds())


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


# ---------- Зависимости ----------

security_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    """Возвращает пользователя, если токен передан и валиден, иначе None."""
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload.get('sub'))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def get_current_user(
    user: Optional[models.User] = Depends(get_current_user_optional),
) -> models.User:
    """Требует валидный токен. Если нет — 401."""
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication required')
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    """Требует группу admin. Иначе — 403."""
    if user.group != 'admin':
        raise HTTPException(status_code=403, detail='Admin rights required')
    return user