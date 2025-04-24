from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, Field


class Notification(Document):
    id: UUID = Field(default_factory=uuid4)
    message: str
    recipient_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"

    class Config:
        schema_extra = {
            "example": {
                "message": "You have successfully registered.",
                "recipient_id": "e3a9f2f1-3df3-44f0-a2ee-58d2c0ea9aa3",
            }
        }


class NotificationCreate(BaseModel):
    message: str
    recipient_id: UUID
