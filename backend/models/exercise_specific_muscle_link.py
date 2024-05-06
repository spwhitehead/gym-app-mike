

from sqlmodel import SQLModel, Field, Column, Relationship, Integer, ForeignKey


class ExerciseSpecificMuscleLink(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    exercise_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
    specific_muscle_id: int | None = Field(default=None, foreign_key="specificmuscle.id")

    exercise: 'Exercise' = Relationship(back_populates="specific_muscles")
    specific_muscle: 'SpecificMuscle' = Relationship(back_populates="exercise_links")

    def __hash__(self):
        return hash((self.exercise_id, self.specific_muscle_id))
    
    def __eq__(self, other):
        if isinstance(other, ExerciseSpecificMuscleLink):
            return (self.exercise_id == other.exercise_id and self.specific_muscle_id == other.specific_muscle_id)

from models.unique_data import SpecificMuscle
from models.exercise import Exercise