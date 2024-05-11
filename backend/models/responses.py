from uuid import UUID
from sqlmodel import SQLModel
from models.exercise_log import ExerciseLogBase
from models.exercise import ExerciseBase 
from models.workout_exercise import WorkoutExerciseBase
from models.workout import WorkoutBase
from models.user import UserBase
from models.relationship_merge import Exercise


class ExerciseResponseData(ExerciseBase):
    uuid: UUID
    workout_category: str | None
    movement_category: str | None
    equipment: str | None
    major_muscle: str | None
    specific_muscles: list[str] | None

    @classmethod
    def from_orm(cls, db_obj: Exercise):
        return cls(
            uuid = db_obj.uuid,
            name = db_obj.name,
            description = db_obj.description,
            workout_category = db_obj.workout_category.name if db_obj.workout_category else None,
            movement_category = db_obj.movement_category.name if db_obj.movement_category else None,
            equipment = db_obj.equipment.name if db_obj.equipment else None,
            major_muscle = db_obj.major_muscle.name if db_obj.major_muscle else None,
            specific_muscles = [specific_muscle.name for specific_muscle in db_obj.specific_muscles]
        )

class ExerciseResponse(SQLModel):
    data: ExerciseResponseData
    detail: str

class ExerciseListResponse(SQLModel):
    data: list[ExerciseResponseData]
    detail: str

class ExerciseLogResponseData(ExerciseLogBase):
    uuid: UUID
    user_uuid: UUID
    exercise: 'ExerciseResponseData'
    
class ExerciseLogResponse(SQLModel):
    data: 'ExerciseLogResponseData'
    detail: str

class ExerciseLogListResponse(SQLModel):
    data: list[ExerciseLogResponseData]
    detail: str

class WorkoutExerciseResponseData(WorkoutExerciseBase):
    uuid: UUID
    exercise_order: int | None
    exercise: 'ExerciseResponseData'

class WorkoutExerciseResponse(SQLModel):
    data: WorkoutExerciseResponseData
    detail: str
    
class WorkoutExerciseListResponse(SQLModel):
    data: list[WorkoutExerciseResponseData] 
    detail: str

class WorkoutResponseData(WorkoutBase):
    uuid: UUID
    workout_exercises: list['WorkoutExerciseResponseData']

class WorkoutResponse(SQLModel):
    data: WorkoutResponseData
    detail: str

class WorkoutListResponse(SQLModel):
    data: list[WorkoutResponseData]
    detail: str

class UserResponseData(UserBase):
    uuid: UUID
    roles: list[str]
    
class UserResponse(SQLModel):
    data: UserResponseData
    detail: str

class UserListResponse(SQLModel):
    data: list[UserResponseData]
    detail: str
