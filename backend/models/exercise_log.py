from uuid import UUID
from uuid import uuid4 as new_uuid
from datetime import datetime

from pydantic import field_validator
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey, CHAR, String

from models.enums import ResistanceType

class ExerciseLogBase(SQLModel):
    datetime_completed: datetime
    exercise_uuid: str = Field(default=None, sa_column=Column(String, ForeignKey("exercise.uuid", ondelete="CASCADE")))
    resistance_type: ResistanceType = Field(sa_column=Column(SQLEnum(ResistanceType)))
    sets: int
    reps: int
    weight: float

    @field_validator("resistance_type", mode="before", check_fields=False)
    def convert_str_to_resistance_type(cls, value: str) -> ResistanceType:
        valid_values = ', '.join(resistance_type.value for resistance_type in ResistanceType)
        if not isinstance(value, str):
            raise TypeError(f"resistance_type must be a string with a value of one of these items: {valid_values}")
        try:
            return ResistanceType[value.upper()]
        except KeyError as e:
            raise ValueError(f"resistance_type must be one of: {valid_values}. Error: {str(e)}")
    
    @field_validator("exercise_uuid", mode="before", check_fields=False)
    def convert_exercise_uuid_to_str(cls, value: UUID) -> str:
        if isinstance(value, UUID):
            try:
                return str(value)
            except ValueError as e:
               raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
        else:
            return value
    

class ExerciseLog(ExerciseLogBase, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default_factory=lambda: str(new_uuid()), sa_column=Column(CHAR(32), unique=True))

    exercise: 'Exercise' = Relationship(back_populates="exercise_logs")
    
    @field_validator("uuid", mode="before", check_fields=False)
    def convert_uuid_to_str(cls, value: UUID) -> str:
        if isinstance(value, UUID):
            try:
                return str(value)
            except ValueError as e:
               raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
        else:
            return value

class ExerciseLogCreateReq(ExerciseLogBase):
    exercise_uuid: UUID

    @field_validator('exercise_uuid', mode="before", check_fields=False)
    def convert_str_to_exercise_uuid(cls, value: str) -> UUID:
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError as e:
                raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
        else:
            return value


class ExerciseLogUpdateReq(ExerciseLogBase):
    datetime_completed: datetime | None = None
    exercise_uuid: UUID | None = None
    resistance_type: ResistanceType | None = None
    sets: int | None = None
    reps: int | None = None
    weight: float | None = None

    @field_validator('uuid', mode="before", check_fields=False)
    def convert_str_to_UUID(cls, value: str) -> UUID:
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError as e:
                raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
        else:
            return value

class ExerciseLogResponseData(ExerciseLogBase):
    uuid: UUID
    exercise: 'ExerciseResponseData'

    @field_validator('uuid', mode="before", check_fields=False)
    def convert_str_to_uuid(cls, value: str) -> UUID:
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError as e:
                raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
        else:
            return value
    
class ExerciseLogResponse(SQLModel):
    data: ExerciseLogResponseData
    detail: str

class ExerciseLogListResponse(SQLModel):
    data: list[ExerciseLogResponseData]
    detail: str

from models.exercise import Exercise, ExerciseResponseData