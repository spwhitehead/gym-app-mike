from uuid import UUID
from sqlmodel import SQLModel, Field, Enum as SQLEnum

from models.enums import BandColor


class ResistanceBand(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True, index=True)
    uuid: UUID | None = Field(default = None, unique=True, index=True)
    color: BandColor = Field(sa_column=SQLEnum(BandColor))
    resistance_weight: float

