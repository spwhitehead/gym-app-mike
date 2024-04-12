from enum import Enum
from datetime import date
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel, Column, Enum as SQLEnum

# Enums
class MuscleGroup(str, Enum):
    CHEST = "Chest"
    BACK = "Back"
    SHOULDERS = "Shoulders"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    LEGS = "Legs"
    QUADRICEPS = "Quadriceps"
    HAMSTRINGS = "Hamstrings"
    CALVES = "Calves"
    GLUTES = "Glutes"
    ABDOMINALS = "Abdominals"
    FOREARMS = "Forearms" 
    OBLIQUES = "Obliques"
    LATS = "Lats"

class BandColor(str, Enum):
    YELLOW = "yellow"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    BLACK = "black"
    PURPLE = "purple"
    ORANGE = "orange"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class WeightUnits(str, Enum):
    KILOGRAMS = "kg"
    LBS = "lbs"
    
class HeightUnits(str, Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"

class ResistenceType(str, Enum):
    DUMBBELL = "dumbbell"
    BARBELL = "barbell"
    BAND = "band"


# Classes
class ResistanceBand(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    uuid: UUID | None = Field(default = None, unique=True)
    color: BandColor = Field(sa_column=SQLEnum(BandColor))
    resistance_weight: float

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

class WorkoutPlanExerciseLink(SQLModel, table=True):
    workout_plan_id: int = Field(foreign_key="workoutplan.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)

class WorkoutPlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    name: str
    description: str
    exercises: list[Exercise] = Relationship(link_model=WorkoutPlanExerciseLink)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default=None, unique=True)
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender

class CreateWorkoutPlanRequest(BaseModel):
    name: str
    description: str

class UpdateWorkoutPlanRequest(BaseModel):
    name: str = None
    description: str = None

class WorkoutPlanResponse(BaseModel):
    uuid: UUID
    name: str
    description: str
    exercises: list[Exercise] = []

class Response(BaseModel):
    data: WorkoutPlanResponse | list[WorkoutPlanResponse]
    message: str