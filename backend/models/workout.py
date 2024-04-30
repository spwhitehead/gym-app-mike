from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, ForeignKey, CHAR

from models.utility import GUID



class WorkoutBase(SQLModel):
    name: str
    description: str

class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    workout_exercises: list['WorkoutExercise'] = Relationship(back_populates="workout")

    # @field_validator("uuid", mode="before", check_fields=False)
    # def convert_uuid_to_str(cls, value: UUID) -> str:
    #     if isinstance(value, UUID):
    #         try:
    #             return str(value)
    #         except ValueError as e:
    #            raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
    #     else:
    #         return value

class WorkoutCreateReq(WorkoutBase):
    pass

class WorkoutUpdateReq(WorkoutBase):
    name: str | None = None
    description: str | None = None

class WorkoutAddWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID

class WorkoutRemoveWorkoutExerciseReq(SQLModel):
    workout_exercise_uuid: UUID

class WorkoutResponseData(WorkoutBase):
    uuid: UUID
    workout_exercises: list['WorkoutExercise']

    # @field_validator('uuid', mode="before", check_fields=False)
    # def convert_str_to_UUID(cls, value: str) -> UUID:
    #     if isinstance(value, str):
    #         try:
    #             return UUID(value)
    #         except ValueError as e:
    #             raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
    #     else:
    #         return value
class WorkoutResponse(SQLModel):
    data: WorkoutResponseData
    detail: str
class WorkoutListResponse(SQLModel):
    data: list[WorkoutResponseData]
    detail: str

# Late import
from models.workout_exercise import WorkoutExercise 