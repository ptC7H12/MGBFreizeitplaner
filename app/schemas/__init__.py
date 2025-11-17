"""Pydantic Schemas für Validierung"""
from app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from app.schemas.family import FamilyCreate, FamilyUpdate, FamilyResponse
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from app.schemas.setting import SettingUpdate, SettingResponse
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.ruleset import RulesetCreate, RulesetUpdate, RulesetResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

# Aliase für Kompatibilität mit älterem Code
ParticipantCreateSchema = ParticipantCreate
ParticipantUpdateSchema = ParticipantUpdate
FamilyCreateSchema = FamilyCreate
FamilyUpdateSchema = FamilyUpdate
PaymentCreateSchema = PaymentCreate
PaymentUpdateSchema = PaymentUpdate
ExpenseCreateSchema = ExpenseCreate
ExpenseUpdateSchema = ExpenseUpdate
IncomeCreateSchema = IncomeCreate
IncomeUpdateSchema = IncomeUpdate
SettingUpdateSchema = SettingUpdate
EventCreateSchema = EventCreate
EventUpdateSchema = EventUpdate
RoleCreateSchema = RoleCreate
RoleUpdateSchema = RoleUpdate
RulesetCreateSchema = RulesetCreate
RulesetUpdateSchema = RulesetUpdate
TaskCreateSchema = TaskCreate
TaskUpdateSchema = TaskUpdate

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
    "IncomeCreate",
    "IncomeUpdate",
    "IncomeResponse",
    "IncomeCreateSchema",
    "IncomeUpdateSchema",
    "SettingUpdate",
    "SettingResponse",
    "SettingUpdateSchema",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "EventCreateSchema",
    "EventUpdateSchema",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleCreateSchema",
    "RoleUpdateSchema",
    "RulesetCreate",
    "RulesetUpdate",
    "RulesetResponse",
    "RulesetCreateSchema",
    "RulesetUpdateSchema",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskCreateSchema",
    "TaskUpdateSchema",
]
