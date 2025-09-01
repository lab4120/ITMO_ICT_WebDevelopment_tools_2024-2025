from typing import Optional
from pydantic import BaseModel

class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int

class UserNotificationRead(BaseModel):
    user_id: int
    notification_id: int
    is_read: bool 