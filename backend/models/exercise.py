from datetime import datetime
from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import SQLModel, Field, Column, Relationship, Integer, ForeignKey, Text

from models.utility import GUID



class ExerciseBase(SQLModel):
    name: str 
    description: str = Field(Column(Text)) 

class ExerciseMaster(ExerciseBase):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    workout_category_id: int | None = Field(default=None, foreign_key="workoutcategory.id")
    movement_category_id: int | None = Field(default=None, foreign_key="movementcategory.id")
    equipment_id: int | None = Field(default=None, foreign_key="equipment.id")
    major_muscle_id: int | None = Field(default=None, foreign_key="majormuscle.id")
    

class ExerciseCreateReq(ExerciseBase):
    workout_category: str 
    movement_category: str 
    equipment: str 
    major_muscle: str 
    specific_muscles: list[str] 

class ExercisePatchReq(ExerciseBase):
    name: str | None = None
    description: str | None = None
    workout_category: str | None = None
    movement_category: str | None = None
    equipment: str | None = None
    major_muscle: str | None = None
    specific_muscles: list[str] | None = None




class ExerciseLogBase(SQLModel):
    datetime_completed: datetime
    reps: int
    weight: float

class ExerciseLogCreateReq(ExerciseLogBase):
    exercise_uuid: UUID

class ExerciseLogPatchReq(ExerciseLogBase):
    datetime_completed: datetime | None = None
    exercise_uuid: UUID | None = None
    reps: int | None = None
    weight: float | None = None
