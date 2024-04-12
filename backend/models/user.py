from datetime import date
from enum import Enum
from uuid import UUID

from sqlmodel import SQLModel, Field

from models.enums import Gender

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender

