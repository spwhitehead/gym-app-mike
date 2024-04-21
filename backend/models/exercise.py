from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, Relationship, Integer, ForeignKey, CHAR

from models.enums import WorkoutCategory, MajorMuscleGroup, SpecificMuscleGroup, MovementCategory

class ExerciseMajorMuscleLink(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    exercise_id: int = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
    major_muscle_group: MajorMuscleGroup = Field(sa_column=Column(SQLEnum(MajorMuscleGroup)))

    exercise: 'Exercise' = Relationship(sa_relationship=relationship("Exercise", back_populates="major_muscles"))

class ExerciseSpecificMuscleLink(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    exercise_id: int = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE")))
    specific_muscle_group: SpecificMuscleGroup = Field(sa_column=Column(SQLEnum(SpecificMuscleGroup)))

    exercise: 'Exercise' = Relationship(sa_relationship=relationship("Exercise", back_populates="specific_muscles"))

class ExerciseBase(SQLModel):
    name: str
    description: str
    workout_category: WorkoutCategory = Field(sa_column=Column(SQLEnum(WorkoutCategory)))
    movement_category: MovementCategory = Field(sa_column=Column(SQLEnum(MovementCategory)))
    
    @field_validator("movement_category", mode="before", check_fields=False)
    def convert_str_to_workout_category(cls, value: str) -> MovementCategory:
        valid_values = ', '.join(resistance_type.value for resistance_type in MovementCategory)
        if not isinstance(value, str):
            raise TypeError(f"resistance_type must be a string with a value of one of these items: {valid_values}")
        try:
            return MovementCategory[value.upper()]
        except KeyError as e:
            raise ValueError(f"resistance_type must be one of: {valid_values}. Error: {str(e)}")

class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default_factory=lambda: str(new_uuid()), sa_column=Column(CHAR(32), unique=True))
    major_muscles: list['ExerciseMajorMuscleLink'] = Relationship(sa_relationship=relationship("ExerciseMajorMuscleLink", back_populates="exercise", cascade="all, delete, delete-orphan"))
    specific_muscles: list['ExerciseSpecificMuscleLink'] = Relationship(sa_relationship=relationship("ExerciseSpecificMuscleLink", back_populates="exercise", cascade="all, delete, delete-orphan"))

    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="exercise")

    @field_validator("uuid", mode="before", check_fields=False)
    def convert_uuid_to_str(cls, value: UUID) -> str:
        if isinstance(value, UUID):
            try:
                return str(value)
            except ValueError as e:
               raise ValueError(f"UUID must be a valid UUID to convert to str. Value: {value} is of type {type(value)}, Error: {e}") 
        else:
            return value
class ExerciseCreateReq(ExerciseBase):
    major_muscles: list[MajorMuscleGroup]
    specific_muscles: list[SpecificMuscleGroup]

    @field_validator("major_muscles", mode="before", check_fields=False)
    def convert_str_to_major_muscle_group(cls, values: list[str]) -> list[MajorMuscleGroup]:
        if not isinstance(values, list):
            raise TypeError("major_muscles must be a list of Msucle Group values.") 
        try:
            return [MajorMuscleGroup[item.upper()] for item in values]
        except KeyError as e:
            valid_values = ', '.join(muscle.value for muscle in MajorMuscleGroup)
            raise ValueError(f"Each item in 'major_muscles' must be of one of: {valid_values}. Error: {str(e)}")

    @field_validator("specific_muscles", mode="before", check_fields=False)
    def convert_str_to_specific_muscle_group(cls, values: list[str]) -> list[SpecificMuscleGroup]:
        if not isinstance(values, list):
            raise TypeError("specific_muscles must be a list of Msucle Group values.") 
        try:
            return [SpecificMuscleGroup["_".join(item.upper().split(" "))] for item in values]
        except KeyError as e:
            valid_values = ', '.join(muscle.value for muscle in SpecificMuscleGroup)
            raise ValueError(f"Each item in 'specific_muscles' must be of one of: {valid_values}. Error: {str(e)}")
    
    @field_validator("workout_category", mode="before", check_fields=False)
    def convert_str_to_workout_category(cls, value: str) -> WorkoutCategory:
        valid_values = ', '.join(workout_category.value for workout_category in WorkoutCategory)
        if not isinstance(value, str):
            raise TypeError(f"workout_category must be a string with a value of one of these items: {valid_values}")
        try:
            return WorkoutCategory[value.upper()]
        except KeyError as e:
            raise ValueError(f"workout_category must be one of: {valid_values}. Error: {str(e)}")
    
class ExerciseUpdateReq(ExerciseBase):
    name: str | None = None
    description: str | None = None
    major_muscles: list[MajorMuscleGroup] = None
    specific_muscles: list[SpecificMuscleGroup] = None
    
    @field_validator("major_muscles", mode="before", check_fields=False)
    def convert_str_to_major_muscle_group(cls, values: list[str]) -> list[MajorMuscleGroup]:
        if not isinstance(values, list):
            raise TypeError("major_muscles must be a list of Msucle Group values.") 
        try:
            return [MajorMuscleGroup[item.upper()] for item in values]
        except KeyError as e:
            valid_values = ', '.join(muscle.value for muscle in MajorMuscleGroup)
            raise ValueError(f"Each item in 'major_muscles' must be of one of: {valid_values}. Error: {str(e)}")

    @field_validator("specific_muscles", mode="before", check_fields=False)
    def convert_str_to_specific_muscle_group(cls, values: list[str]) -> list[SpecificMuscleGroup]:
        if not isinstance(values, list):
            raise TypeError("specific_muscles must be a list of Msucle Group values.") 
        try:
            return [SpecificMuscleGroup["_".join(item.upper().split(" "))] for item in values]
        except KeyError as e:
            valid_values = ', '.join(muscle.value for muscle in SpecificMuscleGroup)
            raise ValueError(f"Each item in 'specific_muscles' must be of one of: {valid_values}. Error: {str(e)}")
    
    @field_validator("workout_category", mode="before", check_fields=False)
    def convert_str_to_workout_category(cls, value: str) -> WorkoutCategory:
        valid_values = ', '.join(resistance_type.value for resistance_type in WorkoutCategory)
        if not isinstance(value, str):
            raise TypeError(f"resistance_type must be a string with a value of one of these items: {valid_values}")
        try:
            return WorkoutCategory[value.upper()]
        except KeyError as e:
            raise ValueError(f"resistance_type must be one of: {valid_values}. Error: {str(e)}")
    
    
class ExerciseResponseData(ExerciseBase):
    uuid: UUID
    major_muscles: list[str]
    specific_muscles: list[str]

    @field_validator('specific_muscles', mode="before", check_fields=False)
    def extract_specific_muscle_names(cls, value: list[ExerciseSpecificMuscleLink]) -> list[str]:
        target_muscles: list[str] = []
        for link in value:
            if isinstance(link, ExerciseSpecificMuscleLink):
                print(link.specific_muscle_group.value)
                target_muscles.append(link.specific_muscle_group.value)
        return target_muscles
    
    @field_validator('major_muscles', mode="before", check_fields=False)
    def extract_major_muscle_names(cls, value: list[ExerciseMajorMuscleLink]) -> list[str]:
        target_muscles: list[str] = []
        for link in value:
            if isinstance(link, ExerciseMajorMuscleLink):
                print(link.major_muscle_group.value)
                target_muscles.append(link.major_muscle_group.value)
        return target_muscles
    
    
    @field_validator('uuid', mode="before", check_fields=False)
    def convert_str_to_UUID(cls, value: str) -> UUID:
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError as e:
                raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
        else:
            return value

class ExerciseResponse(SQLModel):
    data: ExerciseResponseData
    detail: str

class ExerciseListResponse(SQLModel):
    data: list[ExerciseResponseData]
    detail: str

from models.exercise_log import ExerciseLog