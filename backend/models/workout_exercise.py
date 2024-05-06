from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, ForeignKey, Relationship, Integer

from models.utility import GUID


class WorkoutExerciseBase(SQLModel):
    planned_sets: int
    planned_reps: int
    planned_resistance_weight: float  
    
class WorkoutExercise(WorkoutExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    workout_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("workout.id", ondelete="CASCADE")))
    exercise_uuid: UUID = Field(default=None, sa_column=Column(GUID(), ForeignKey("exercise.uuid", ondelete="CASCADE")))
    user_uuid: UUID | None = Field(default=None, sa_column=Column(GUID(), ForeignKey("user.uuid", ondelete="CASCADE")))
    workout: 'Workout' = Relationship(back_populates="workout_exercises")
    

class WorkoutExerciseCreateReq(WorkoutExerciseBase):
    exercise_uuid: UUID

class WorkoutExercisePatchReq(WorkoutExerciseBase):
    exercise_uuid: UUID | None = None
    planned_sets: int | None = None
    planned_reps: int | None = None
    planned_resistance_weight: float | None = None

class WorkoutExerciseResponseData(WorkoutExerciseBase):
    uuid: UUID
    exercise: 'ExerciseResponseData'

class WorkoutExerciseResponse(SQLModel):
    data: WorkoutExerciseResponseData
    detail: str
    
class WorkoutExerciseListResponse(SQLModel):
    data: list[WorkoutExerciseResponseData] 
    detail: str

# Late import
from models.workout import Workout
from models.exercise import ExerciseResponseData