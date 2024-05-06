from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import SQLModel, Field, Relationship, Column, Integer, ForeignKey, CHAR

from models.utility import GUID



class WorkoutBase(SQLModel):
    name: str
    description: str

class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    user_uuid: UUID | None = Field(default=None, sa_column=Column(GUID(), ForeignKey("user.uuid", ondelete="CASCADE")))

    workout_exercises: list['WorkoutExercise'] = Relationship(back_populates="workout")


class WorkoutCreateReq(WorkoutBase):
    pass

class WorkoutPatchReq(WorkoutBase):
    name: str | None = None
    description: str | None = None

class WorkoutAddWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID

class WorkoutRemoveWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID

class WorkoutResponseData(WorkoutBase):
    uuid: UUID
    workout_exercises: list['WorkoutExerciseResponseData']

class WorkoutResponse(SQLModel):
    data: WorkoutResponseData
    detail: str
class WorkoutListResponse(SQLModel):
    data: list[WorkoutResponseData]
    detail: str

# Late import
from models.workout_exercise import WorkoutExerciseResponseData, WorkoutExercise