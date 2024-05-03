from uuid import UUID
from uuid import uuid4 as new_uuid

from sqlmodel import SQLModel, Field, Column, Relationship

from models.utility import GUID

class ExerciseBase(SQLModel):
    name: str = "Bench Press"
    description: str = "Bench Press Description"

class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))
    workout_category_id: int | None = Field(default=None, foreign_key="workoutcategory.id")
    movement_category_id: int | None = Field(default=None, foreign_key="movementcategory.id")
    equipment_id: int | None = Field(default=None, foreign_key="equipment.id")
    major_muscle_id: int | None = Field(default=None, foreign_key="majormuscle.id")
    
    workout_category: 'WorkoutCategory' = Relationship(back_populates="exercises", sa_relationship_kwargs={"lazy":"selectin"})
    movement_category: 'MovementCategory' = Relationship(back_populates="exercises", sa_relationship_kwargs={"lazy":"selectin"})
    major_muscle: 'MajorMuscle' = Relationship(back_populates="exercises", sa_relationship_kwargs={"lazy":"selectin"})
    equipment: 'Equipment' = Relationship(back_populates='exercises', sa_relationship_kwargs={"lazy":"selectin"})

    specific_muscles: list['ExerciseSpecificMuscleLink'] = Relationship(back_populates="exercise")
    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="exercise", sa_relationship_kwargs={"lazy":"selectin"})

class ExerciseCreateReq(ExerciseBase):
    workout_category: str = "Upper"
    movement_category: str = "Press"
    equipment: str = "Barbell"
    major_muscle: str = "Chest"
    specific_muscles: list[str] = ["Middle Chest", "Triceps"]

class ExercisePatchReq(ExerciseBase):
    name: str | None = None
    description: str | None = None
    workout_category: str | None = None
    movement_category: str | None = None
    equipment: str | None = None
    major_muscle: str | None = None
    specific_muscles: list[str] | None = None

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
            specific_muscles = [specific_muscle_link.specific_muscle.name for specific_muscle_link in db_obj.specific_muscles]
        )

    

class ExerciseResponse(SQLModel):
    data: ExerciseResponseData
    detail: str

class ExerciseListResponse(SQLModel):
    data: list[ExerciseResponseData]
    detail: str


from models.exercise_specific_muscle_link import ExerciseSpecificMuscleLink
from models.unique_data import MajorMuscle, MovementCategory, WorkoutCategory, Equipment
from models.exercise_log import ExerciseLog