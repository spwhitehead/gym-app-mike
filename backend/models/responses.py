from datetime import date
from uuid import UUID 


from pydantic import BaseModel

from models.exercise import Exercise, ExerciseMuscleLink
from models.enums import Gender

# Response Data Models
class WorkoutData(BaseModel):
    uuid: UUID
    name: str
    description: str
    exercises: list[Exercise] = []

class UserData(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender
    
class ExerciseData(BaseModel):
    uuid: UUID
    name: str
    description: str
    target_muscles: list[str]
    
# Response Models
class ResponseWorkout(BaseModel):
    data: WorkoutData
    detail: str

class ResponseWorkoutList(BaseModel):
    data: list[WorkoutData]
    detail: str

class ResponseExercise(BaseModel):
    data: ExerciseData
    detail: str

class ResponseExerciseList(BaseModel):
    data: list[ExerciseData]
    detail: str
    
class ResponseUser(BaseModel):
    data: UserData
    detail: str

class ResponseUserList(BaseModel):
    data: list[UserData]
    detail: str