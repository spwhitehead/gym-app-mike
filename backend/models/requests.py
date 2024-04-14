from datetime import date
from uuid import UUID

from pydantic import BaseModel

from models.enums import Gender, MuscleGroup, ResistanceType

# Workout Request
class CreateWorkoutRequest(BaseModel):
    name: str
    description: str
class UpdateWorkoutRequest(BaseModel):
    name: str = None
    description: str = None

# User Request
class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender    
class UpdateUserRequest(BaseModel):
    first_name: str = None
    last_name: str = None
    birthday: date = None
    body_weight: float = None
    height: int = None
    gender: Gender = None

# Exercise Request
class CreateExerciseRequest(BaseModel):
     name: str
     description: str
     target_muscles: list[MuscleGroup] 

class UpdateExerciseRequest(BaseModel):
    name: str = None
    description: str = None
    target_muscles: list[MuscleGroup] = None

#Workout Exercise Request
class CreateWorkoutExerciseRequest(BaseModel):
    name: str
    description: str
    exercise_uuid: UUID
    sets: int
    reps: int
    resistance_type: ResistanceType
    resistance_weight: float
class UpdateWorkoutExerciseRequest(BaseModel):
    name: str = None
    description: str = None
    exercise_uuid: UUID = None
    sets: int = None
    reps: int = None
    resistance_type: ResistanceType = None
    resistance_weight: float = None
 