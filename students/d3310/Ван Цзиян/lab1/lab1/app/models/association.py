from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class UserNotification(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    notification_id: Optional[int] = Field(default=None, foreign_key="notification.id", primary_key=True)
    is_read: bool = Field(default=False)

    user: "User" = Relationship(back_populates="notifications")
    notification: "Notification" = Relationship(back_populates="users")

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    users: List["UserNotification"] = Relationship(back_populates="notification") 