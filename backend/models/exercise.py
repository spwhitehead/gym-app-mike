from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import SQLModel, Field, Column, Text, Integer, ForeignKey

from utilities.guid import GUID


class ExerciseBase(SQLModel):
    name: str 
    description: str = Field(Column(Text)) 

class ExerciseTableBase(ExerciseBase):
    id: int | None = Field(default=None, primary_key=True, index=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True, index=True))
    image_url: str | None = Field(default=None)
    workout_category_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("workoutcategory.id", ondelete="CASCADE"), index = True))
    movement_category_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("movementcategory.id", ondelete="CASCADE"), index = True))
    equipment_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), index = True))
    major_muscle_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("majormuscle.id", ondelete="CASCADE"), index = True))
    user_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True))
    

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

