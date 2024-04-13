from datetime import date

from pydantic import BaseModel

from models.enums import Gender, MuscleGroup

class CreateWorkoutRequest(BaseModel):
    name: str
    description: str

class UpdateWorkoutRequest(BaseModel):
    name: str = None
    description: str = None

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

class CreateExerciseRequest(BaseModel):
     name: str
     description: str
     target_muscles: list[MuscleGroup] 

class UpdateExerciseRequest(BaseModel):
    name: str = None
    description: str = None
    target_muscles: list[MuscleGroup] = None