from uuid import UUID

from sqlmodel import SQLModel, Field

from models.enums import ResistanceType


class WorkoutExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    exercise_uuid: int = Field(default=None, foreign_key="exercise.uuid")
    sets: int
    reps: int
    resistance_type: ResistanceType
    resistance_weight: float
