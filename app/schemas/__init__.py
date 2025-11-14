"""Pydantic Schemas für Validierung"""
from app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from app.schemas.family import FamilyCreate, FamilyUpdate, FamilyResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse

# Aliase für Kompatibilität mit älterem Code
ParticipantCreateSchema = ParticipantCreate
ParticipantUpdateSchema = ParticipantUpdate

__all__ = [
    "ParticipantCreate",
    "ParticipantUpdate",
    "ParticipantResponse",
    "ParticipantCreateSchema",
    "ParticipantUpdateSchema",
    "FamilyCreate",
    "FamilyUpdate",
    "FamilyResponse",
    "PaymentCreate",
    "PaymentResponse",
    "ExpenseCreate",
    "ExpenseResponse",
]
