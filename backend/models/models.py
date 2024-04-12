from enum import Enum
from dataclasses import dataclass
from datetime import date
from uuid import UUID
from uuid import uuid4 as new_uuid

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
    id: UUID | None = Field(default = None, primary_key=True)
    color: BandColor = Field(sa_column=SQLEnum(BandColor))
    resistance_weight: float

class ExerciseMuscleLink(SQLModel, table=True):
    exercise_id: UUID | None = Field(default = None, foreign_key="exercise.id", primary_key=True)
    exercises: 'Exercise' = Relationship(back_populates="target_muscles")
    musclegroup: MuscleGroup = Field(sa_column=Column(SQLEnum(MuscleGroup), primary_key=True))

class Exercise(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    name: str
    description: str
    target_muscles: list[ExerciseMuscleLink] = Relationship(back_populates="exercises")

class SingleWorkout(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    name: str
    description: str
    exercise_id: UUID = Field(default=None, foreign_key="exercise.id")
    exercise: Exercise = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    sets: int
    reps: int
    resistence_type: ResistenceType
    resistence_weight: float

class WorkoutPlanExerciseLink(SQLModel, table=True):
    workout_plan_id: UUID = Field(foreign_key="workoutplan.id", primary_key=True)
    exercise_id: UUID = Field(foreign_key="exercise.id", primary_key=True)

class WorkoutPlan(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    name: str
    description: str
    exercises: list[Exercise] = Relationship(link_model=WorkoutPlanExerciseLink)
    
    def create_response(id: UUID, name: str, description: str, exercises: list[Exercise] = []):
        return {"data": {"id": id, "name": name, "description": description, "exercises": exercises, "response_message": "Workout Plan created successfully."}}
    
    def update_response(id: UUID, name: str, description: str, exercises: list[Exercise] = []):
        return {"data": {"id": id, "name": name, "description": description, "exercises": exercises, "response_message": "Workout Plan updated successfully."}}
    
    def delete_response(id: UUID, name: str, description: str, exercises: list[Exercise] = []):
        return {"data": {"id": id, "name": name, "description": description, "exercises": exercises, "response_message": "Workout Plan deleted."}}

class User(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
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
 