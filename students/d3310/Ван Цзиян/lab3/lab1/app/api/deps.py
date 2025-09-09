from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User

# Изменение конфигурации OAuth2PasswordBearer для поддержки прямого ввода Bearer токена
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login",
    scheme_name="JWT",
    description="Введите JWT токен для аутентификации. Формат: Bearer YOUR_TOKEN_HERE"
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    username: str = payload["sub"]
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user 