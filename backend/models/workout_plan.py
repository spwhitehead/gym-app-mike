from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from models.exercise import Exercise

class WorkoutPlanExerciseLink(SQLModel, table=True):
    workout_plan_id: int = Field(foreign_key="workoutplan.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)


class WorkoutPlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    exercises: list[Exercise] = Relationship(link_model=WorkoutPlanExerciseLink)

