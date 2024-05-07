from uuid import UUID
from uuid import uuid4 as new_uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey, Integer

from models.utility import GUID

class ExerciseLogBase(SQLModel):
    datetime_completed: datetime
    reps: int
    weight: float

class ExerciseLogMaster(ExerciseLogBase): 
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    user_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE")))
    exercise_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
    
class ExerciseLogCreateReq(ExerciseLogBase):
    exercise_uuid: UUID

class ExerciseLogPatchReq(ExerciseLogBase):
    datetime_completed: datetime | None = None
    exercise_uuid: UUID | None = None
    reps: int | None = None
    weight: float | None = None

