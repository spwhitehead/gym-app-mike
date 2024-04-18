from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, ForeignKey, CHAR

from models.enums import ResistanceType
from models.exercise import ExerciseResponseData

class WorkoutExerciseBase(SQLModel):
    exercise_uuid: str = Field(default=None, sa_column=Column(CHAR(32), ForeignKey("exercise.uuid", ondelete="CASCADE")))
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
    uuid: str | None = Field(default_factory=lambda: str(new_uuid()), unique=True)



class WorkoutExerciseCreateReq(WorkoutExerciseBase):
    pass

class WorkoutExerciseUpdateReq(WorkoutExerciseBase):
    exercise_uuid: int | None = None
    sets: int | None = None
    reps: int | None = None
    resistance_type: ResistanceType | None = None
    resistance_weight: float | None = None

class WorkoutExerciseResponseData(WorkoutExerciseBase):
    uuid: str
    name: str
    description: str
    exercise_uuid: str
    sets: int
    reps: int
    resistance_type: ResistanceType
    resistance_weight: float
    target_muscles: list[str]

class WorkoutExerciseResponse(SQLModel):
    data: WorkoutExerciseResponseData
    detail: str
    
class WorkoutExerciseListResponse(SQLModel):
    data: list[WorkoutExerciseResponseData] 
    detail: str