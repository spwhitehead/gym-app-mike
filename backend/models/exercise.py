from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey, CHAR

from models.utility import GUID

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

class ExerciseBase(SQLModel):
    name: str = "Bench Press"
    description: str = "Bench Press Description"

class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    workout_category_id: int | None = Field(default=None, foreign_key="workoutcategory.id")
    movement_category_id: int | None = Field(default=None, foreign_key="movementcategory.id")
    equipment_id: int | None = Field(default=None, foreign_key="equipment.id")
    major_muscle_id: int | None = Field(default=None, foreign_key="majormuscle.id")
    
    workout_category: 'WorkoutCategory' = Relationship(back_populates="exercises")
    movement_category: 'MovementCategory' = Relationship(back_populates="exercises")
    major_muscle: 'MajorMuscle' = Relationship(back_populates="exercises")
    equipment: 'Equipment' = Relationship(back_populates='exercises')

    specific_muscles: set['ExerciseSpecificMuscleLink'] = Relationship(sa_relationship=relationship("ExerciseSpecificMuscleLink", back_populates="exercise", cascade="all, delete, delete-orphan", collection_class=set))
    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="exercise")

class ExerciseCreateReq(ExerciseBase):
    workout_category: str = "Upper"
    movement_category: str = "Press"
    equipment: str = "Barbell"
    major_muscle: str = "Chest"
    specific_muscles: list[str] = ["Middle Chest", "Triceps"]

class ExercisePatchReq(ExerciseBase):
    name: str | None = None
    description: str | None = None
    workout_category: str | None = None
    movement_category: str | None = None
    equipment: str | None = None
    major_muscle: str | None = None
    specific_muscles: list[str] | None = None

class ExerciseResponseData(ExerciseBase):
    uuid: UUID
    workout_category: str
    movement_category: str
    equipment: str
    major_muscle: str
    specific_muscles: list[str]

class ExerciseResponse(SQLModel):
    data: ExerciseResponseData
    detail: str

class ExerciseListResponse(SQLModel):
    data: list[ExerciseResponseData]
    detail: str

from models.exercise_log import ExerciseLog
from models.unique_data import MajorMuscle, SpecificMuscle, MovementCategory, WorkoutCategory, Equipment