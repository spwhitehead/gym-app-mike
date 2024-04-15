from uuid import UUID

from sqlmodel import SQLModel, Field, Relationship

from models.workout_exercise import WorkoutExercise

class WorkoutExerciseLink(SQLModel, table=True):
    workout_id: int = Field(foreign_key="workout.id", primary_key=True)
    workout_exercise_id: int = Field(foreign_key="workoutexercise.id", primary_key=True)


class Workout(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    workout_exercises: list[WorkoutExercise] = Relationship(link_model=WorkoutExerciseLink)

