"""Pydantic Schemas für Validierung"""
from app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from app.schemas.family import FamilyCreate, FamilyUpdate, FamilyResponse
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.schemas.setting import SettingUpdate, SettingResponse

# Aliase für Kompatibilität mit älterem Code
ParticipantCreateSchema = ParticipantCreate
ParticipantUpdateSchema = ParticipantUpdate
FamilyCreateSchema = FamilyCreate
FamilyUpdateSchema = FamilyUpdate
PaymentCreateSchema = PaymentCreate
PaymentUpdateSchema = PaymentUpdate
ExpenseCreateSchema = ExpenseCreate
ExpenseUpdateSchema = ExpenseUpdate
SettingUpdateSchema = SettingUpdate

__all__ = [
    "ParticipantCreate",
    "ParticipantUpdate",
    "ParticipantResponse",
    "ParticipantCreateSchema",
    "ParticipantUpdateSchema",
    "FamilyCreate",
    "FamilyUpdate",
    "FamilyResponse",
    "FamilyCreateSchema",
    "FamilyUpdateSchema",
    "PaymentCreate",
    "PaymentUpdate",
    "PaymentResponse",
    "PaymentCreateSchema",
    "PaymentUpdateSchema",
    "ExpenseCreate",
    "ExpenseUpdate",
    "ExpenseResponse",
    "ExpenseCreateSchema",
    "ExpenseUpdateSchema",
    "SettingUpdate",
    "SettingResponse",
    "SettingUpdateSchema",
]
