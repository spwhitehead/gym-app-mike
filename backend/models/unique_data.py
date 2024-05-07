# from sqlmodel import SQLModel, Field, Relationship

# def exercise_muscle_link():
#     from models.exercise_specific_muscle_link import ExerciseSpecificMuscleLink
#     return ExerciseSpecificMuscleLink
# class WorkoutCategory(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)

#     exercises: list['Exercise'] = Relationship(back_populates="workout_category")

# class MovementCategory(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)

#     exercises: list['Exercise'] = Relationship(back_populates="movement_category")

# class BandColor(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)

# class MajorMuscle(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)

#     exercises: list['Exercise'] = Relationship(back_populates="major_muscle")

# class SpecificMuscle(SQLModel, table=True):
#     from models.exercise_specific_muscle_link import ExerciseSpecificMuscleLink
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)
    
#     exercises: list['Exercise'] = Relationship(back_populates="specific_muscle", link_model=exercise_muscle_link())

# class Equipment(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True)
    
#     exercises: list['Exercise'] = Relationship(back_populates="equipment")


# # Late import

# from models.exercise import Exercise