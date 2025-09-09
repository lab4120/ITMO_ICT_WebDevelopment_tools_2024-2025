from sqlmodel import Session, select
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from typing import Optional, List

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.exec(select(User).where(User.username == username)).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.exec(select(User).where(User.email == email)).first()

def get_all_users(db: Session) -> List[User]:
    """Получение списка всех пользователей"""
    return db.exec(select(User)).all()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def change_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 