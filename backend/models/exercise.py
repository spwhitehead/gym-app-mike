from uuid import UUID
from enum import Enum

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship

from models.enums import MuscleGroup, BandColor, ResistenceType

class ExerciseMuscleLink(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    exercise_id: int = Field(default=None, foreign_key="exercise.id")
    musclegroup: MuscleGroup = Field(sa_column=Column(SQLEnum(MuscleGroup)))
    exercises: 'Exercise' = Relationship(back_populates="target_muscles")

class Exercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    target_muscles: list[ExerciseMuscleLink] = Relationship(back_populates="exercises")

class SingleWorkout(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    exercise_id: int = Field(default=None, foreign_key="exercise.id")
    exercise: Exercise = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    sets: int
    reps: int
    resistence_type: ResistenceType
    resistence_weight: float

