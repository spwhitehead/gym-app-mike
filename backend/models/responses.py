from datetime import date
from uuid import UUID 


from sqlmodel import SQLModel


from models.enums import Gender, ResistanceType
from models.workout_exercise import WorkoutExercise

# Response Data Models
class WorkoutData(SQLModel):
    uuid: UUID
    name: str
    description: str
    workout_exercises: list["WorkoutExerciseData"]

class UserData(SQLModel):
    uuid: UUID
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender
    
class ExerciseData(SQLModel):
    uuid: UUID
    name: str
    description: str
    target_muscles: list[str]

class WorkoutExerciseData(SQLModel):
    uuid: UUID
    name: str
    description: str
    exercise: ExerciseData
    sets: int
    reps: int
    resistance_type: ResistanceType
    resistance_weight: float
    
# Response Models
class ResponseWorkout(SQLModel):
    data: WorkoutData
    detail: str

class ResponseWorkoutList(SQLModel):
    data: list[WorkoutData]
    detail: str

class ResponseExercise(SQLModel):
    data: ExerciseData
    detail: str

class ResponseExerciseList(SQLModel):
    data: list[ExerciseData]
    detail: str
    
class ResponseUser(SQLModel):
    data: UserData
    detail: str

class ResponseUserList(SQLModel):
    data: list[UserData]
    detail: str

class ResponseWorkoutExercise(SQLModel):
    data: WorkoutExerciseData
    detail: str

class ResponseWorkoutExerciseList(SQLModel):
    data: list[WorkoutExerciseData]
    detail: str