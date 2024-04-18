from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey

from models.enums import MuscleGroup

class ExerciseMuscleLink(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    exercise_id: int = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
    musclegroup: MuscleGroup = Field(sa_column=Column(SQLEnum(MuscleGroup)))
    exercise: 'Exercise' = Relationship(sa_relationship=relationship("Exercise", back_populates="target_muscles"))

class ExerciseBase(SQLModel):
    name: str
    description: str
    
    @field_validator("target_muscles", mode="before", check_fields=False)
    def convert_str_to_muscle_group(cls, values: list[str]) -> list[MuscleGroup]:
        if not isinstance(values, list):
            raise TypeError("target_muscles must be a list of Msucle Group values.") 
        try:
            return [MuscleGroup[item.upper()] for item in values]
        except KeyError as e:
            valid_values = ', '.join(muscle.value for muscle in MuscleGroup)
            raise ValueError(f"Each item in 'target_muscles' must be of one of: {valid_values}. Error: {str(e)}")
class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default_factory=lambda: str(new_uuid()), unique=True)
    target_muscles: list[ExerciseMuscleLink] = Relationship(sa_relationship=relationship("ExerciseMuscleLink", back_populates="exercise", cascade="all, delete, delete-orphan"))

class ExerciseCreateReq(ExerciseBase):
    target_muscles: list[MuscleGroup]
    
class ExerciseUpdateReq(ExerciseBase):
    name: str | None = None
    description: str | None = None
    target_muscles: list[MuscleGroup] = None
    
class ExerciseResponseData(ExerciseBase):
    uuid: str
    target_muscles: list[str]


    @field_validator('target_muscles', mode="before", check_fields=False)
    def extract_muscle_names(cls, value: list[ExerciseMuscleLink]):
        target_muscles: list[str] = []
        for link in value:
            if isinstance(link, ExerciseMuscleLink):
                target_muscles.append(link.musclegroup.value)
        return target_muscles

class ExerciseResponse(SQLModel):
    data: ExerciseResponseData
    detail: str

class ExerciseListResponse(SQLModel):
    data: list[ExerciseResponseData]
    detail: str