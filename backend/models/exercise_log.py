from uuid import UUID
from uuid import uuid4 as new_uuid
from datetime import datetime

from pydantic import field_validator

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey, CHAR, String

from models.utility import GUID
from models.unique_data import Equipment
    

class ExerciseLogBase(SQLModel):
    datetime_completed: datetime
    user_uuid: UUID | None = Field(default=None, sa_column=Column(GUID(), ForeignKey("user.uuid", ondelete="CASCADE")))
    exercise_uuid: UUID | None = Field(default=None, sa_column=Column(GUID(), ForeignKey("exercise.uuid", ondelete="CASCADE")))
    reps: int
    weight: float

class ExerciseLog(ExerciseLogBase, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    
    exercise: 'Exercise' = Relationship(back_populates="exercise_logs")
    user: 'User' = Relationship(back_populates="exercise_logs")
    
class ExerciseLogCreateReq(ExerciseLogBase):
    exercise_uuid: UUID


class ExerciseLogPatchReq(ExerciseLogBase):
    datetime_completed: datetime | None = None
    exercise_uuid: UUID | None = None
    reps: int | None = None
    weight: float | None = None

class ExerciseLogResponseData(ExerciseLogBase):
    uuid: UUID
    exercise_uuid: UUID
    exercise: 'ExerciseResponseData'
    
class ExerciseLogResponse(SQLModel):
    data: ExerciseLogResponseData
    detail: str

class ExerciseLogListResponse(SQLModel):
    data: list[ExerciseLogResponseData]
    detail: str

from models.exercise import Exercise, ExerciseResponseData
from models.user import User, UserResponseData