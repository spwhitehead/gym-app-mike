from uuid import UUID
from uuid import uuid4 as new_uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, ForeignKey, Integer

from utilities.guid import GUID

class ExerciseLogBase(SQLModel):
    datetime_completed: datetime
    reps: int
    weight: float

class ExerciseLogTableBase(ExerciseLogBase): 
    id: int | None = Field(default=None, primary_key=True, index=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True,  index=True))
    user_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True))
    exercise_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE"), index=True))
    
class ExerciseLogCreateReq(ExerciseLogBase):
    exercise_uuid: UUID

class ExerciseLogPatchReq(ExerciseLogBase):
    datetime_completed: datetime | None = None
    exercise_uuid: UUID | None = None
    reps: int | None = None
    weight: float | None = None

