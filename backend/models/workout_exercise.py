from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlalchemy.orm import relationship
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, ForeignKey, CHAR, Relationship, Integer

from models.enums import ResistanceType
from models.utility import GUID


class WorkoutExerciseBase(SQLModel):
    sets: int
    reps: int
    resistance_type: ResistanceType = Field(sa_column=Column(SQLEnum(ResistanceType)))
    resistance_weight: float  
    
    @field_validator("resistance_type", mode="before", check_fields=False)
    def convert_str_to_resistance_type(cls, value: str) -> ResistanceType:
        valid_values = ', '.join(resistance_type.value for resistance_type in ResistanceType)
        if not isinstance(value, str):
            raise TypeError(f"resistance_type must be a string with a value of one of these items: {valid_values}")
        try:
            return ResistanceType[value.upper()]
        except KeyError as e:
            raise ValueError(f"resistance_type must be one of: {valid_values}. Error: {str(e)}")
    
class WorkoutExercise(WorkoutExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    exercise_uuid: UUID = Field(default=None, sa_column=Column(GUID(), ForeignKey("exercise.uuid", ondelete="CASCADE")))
    workout_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("workout.id", ondelete="CASCADE")))
    workout: 'Workout' = Relationship(back_populates="workout_exercises")
    
    # @field_validator("uuid", "exercise_uuid", mode="before", check_fields=False)
    # def convert_uuid_to_str(cls, value: UUID) -> str:
    #     if isinstance(value, UUID):
    #         try:
    #             return str(value)
    #         except ValueError as e:
    #            raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
    #     else:
    #         return value

class WorkoutExerciseCreateReq(WorkoutExerciseBase):
    exercise_uuid: UUID

class WorkoutExerciseUpdateReq(WorkoutExerciseBase):
    exercise_uuid: UUID | None = None
    sets: int | None = None
    reps: int | None = None
    resistance_type: ResistanceType | None = None
    resistance_weight: float | None = None

class WorkoutExerciseResponseData(WorkoutExerciseBase):
    uuid: UUID
    name: str
    description: str
    exercise_uuid: UUID
    sets: int
    reps: int
    resistance_type: ResistanceType
    resistance_weight: float
    target_muscles: list[str]

    # @field_validator('uuid', 'exercise_uuid', mode="before", check_fields=False)
    # def convert_str_to_UUID(cls, value: str) -> UUID:
    #     if isinstance(value, str):
    #         try:
    #             return UUID(value)
    #         except ValueError as e:
    #             raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
    #     else:
    #         return value

class WorkoutExerciseResponse(SQLModel):
    data: WorkoutExerciseResponseData
    detail: str
    
class WorkoutExerciseListResponse(SQLModel):
    data: list[WorkoutExerciseResponseData] 
    detail: str

# Late import
from models.workout import Workout 