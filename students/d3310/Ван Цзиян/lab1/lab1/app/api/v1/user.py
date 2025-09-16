from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from typing import List
from app.schemas.user import UserCreate, UserRead, UserLogin, UserUpdatePassword
from app.crud.user import create_user, authenticate_user, change_password, get_user_by_username, get_all_users
from app.core.security import create_access_token, verify_password, decode_access_token
from app.db.session import get_session
from app.models.user import User

router = APIRouter()

security = HTTPBearer()

def get_current_user_from_bearer(
    token: str = Depends(security),
    db: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token.credentials)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    
    username: str = payload["sub"]
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_session)) -> UserRead:
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = create_user(db, user.username, user.email, user.password)
    return UserRead.model_validate(db_user, from_attributes=True)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)) -> dict:
    db_user = authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=List[UserRead])
def read_users(db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> List[UserRead]:
    users = get_all_users(db)
    return [UserRead.from_orm(user) for user in users]

@router.get("/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_user_from_bearer)) -> UserRead:
    return UserRead.from_orm(current_user)

@router.post("/change-password")
def change_user_password(data: UserUpdatePassword, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    change_password(db, current_user, data.new_password)
    return {"msg": "Password updated successfully"} 