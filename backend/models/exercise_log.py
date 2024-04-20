from uuid import UUID
from uuid import uuid4 as new_uuid
from datetime import datetime

from pydantic import field_validator
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey, CHAR

from models.enums import ResistanceType

class ExerciseLogBase(SQLModel):
    date: datetime
    exercise_uuid: int = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
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
    
    

class ExerciseLog(ExerciseLogBase, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default_factory=lambda: str(new_uuid()), sa_column=Column(CHAR(32), unique=True))
    
    @field_validator("uuid", mode="before", check_fields=False)
    def convert_uuid_to_str(cls, value: UUID) -> str:
        if isinstance(value, UUID):
            try:
                return str(value)
            except ValueError as e:
               raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
        else:
            return value
    