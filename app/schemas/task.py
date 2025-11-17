"""Pydantic Schemas für Task"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TaskBase(BaseModel):
    """Basis-Schema für Task"""
    task_type: str = Field(..., min_length=1, max_length=100)
    reference_id: int
    is_completed: bool = True
    completion_note: Optional[str] = Field(None, max_length=500)
    event_id: int

    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        """Validiert den Task-Typ"""
        if not v or not v.strip():
            raise ValueError("Task-Typ darf nicht leer sein")
        return v.strip()


class TaskCreate(TaskBase):
    """Schema für das Erstellen einer Task"""
    pass


class TaskUpdate(BaseModel):
    """Schema für das Aktualisieren einer Task"""
    task_type: Optional[str] = Field(None, min_length=1, max_length=100)
    reference_id: Optional[int] = None
    is_completed: Optional[bool] = None
    completion_note: Optional[str] = Field(None, max_length=500)
    event_id: Optional[int] = None

    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Task-Typ"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task-Typ darf nicht leer sein")
        return v.strip() if v else None


class TaskResponse(BaseModel):
    """Schema für die Antwort"""
    id: int
    task_type: str
    reference_id: int
    is_completed: bool
    completion_note: Optional[str]
    event_id: int
    completed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
