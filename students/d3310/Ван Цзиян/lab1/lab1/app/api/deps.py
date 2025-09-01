from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User

# 修改OAuth2PasswordBearer配置，支持直接输入Bearer令牌
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login",
    scheme_name="JWT",
    description="输入JWT令牌进行认证。格式: Bearer YOUR_TOKEN_HERE"
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