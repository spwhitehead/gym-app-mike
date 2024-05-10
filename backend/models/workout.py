from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import (
    SQLModel, Field, Relationship,
    Column, Integer, ForeignKey, CHAR
    )

from utilities.guid import GUID

class WorkoutBase(SQLModel):
    name: str
    description: str
class WorkoutTableBase(WorkoutBase):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True, index=True))
    user_id: int = Field(default=None, sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True))
class WorkoutCreateReq(WorkoutBase):
    pass
class WorkoutPatchReq(WorkoutBase):
    name: str | None = None
    description: str | None = None
class WorkoutAddWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID
class WorkoutRemoveWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID

