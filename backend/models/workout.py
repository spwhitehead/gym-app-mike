from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from models.exercise import Exercise

class WorkoutExerciseLink(SQLModel, table=True):
    workout_id: int = Field(foreign_key="workout.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)


class Workout(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    exercises: list[Exercise] = Relationship(link_model=WorkoutExerciseLink)

