from uuid import UUID
from sqlmodel import SQLModel, Relationship, Field, Column, Integer, ForeignKey
from models.user import UserTableBase
from models.exercise import ExerciseTableBase
from models.exercise_log import ExerciseLogTableBase
from models.workout_exercise import WorkoutExerciseTableBase
from models.workout import WorkoutTableBase

class WorkoutExerciseWorkoutOrderLink(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True)
    workout_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("workout.id", ondelete="CASCADE"), index=True))
    workout_exercise_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("workoutexercise.id", ondelete="CASCADE"), primary_key=True, index=True))
    exercise_order: int
    
class UserRoleLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, index=True))
    role_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True, index=True))

    def __hash__(self):
        return hash((self.user_id, self.role_id))
    
    def __eq__(self, other):
        if isinstance(other, UserRoleLink):
            return (self.user_id == other.user_id and self.role_id == other.role_id)

class ExerciseSpecificMuscleLink(SQLModel, table=True):
    exercise_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("exercise.id", ondelete="CASCADE"), primary_key=True,  index=True))
    specific_muscle_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("specificmuscle.id", ondelete="CASCADE"), primary_key=True, index=True))

    def __hash__(self):
        return hash((self.exercise_id, self.specific_muscle_id))
    
    def __eq__(self, other):
        if isinstance(other, ExerciseSpecificMuscleLink):
            return (self.exercise_id == other.exercise_id and self.specific_muscle_id == other.specific_muscle_id)

class Exercise(ExerciseTableBase, table=True):
    workout_category: 'WorkoutCategory' = Relationship(back_populates="exercises")
    movement_category: 'MovementCategory' = Relationship(back_populates="exercises")
    major_muscle: 'MajorMuscle' = Relationship(back_populates="exercises")
    equipment: 'Equipment' = Relationship(back_populates='exercises')
    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="exercise")

    specific_muscles: list['SpecificMuscle'] = Relationship(back_populates="exercises", link_model=ExerciseSpecificMuscleLink)
    user: 'User' = Relationship(back_populates="exercises")

class ExerciseLog(ExerciseLogTableBase, table=True):
    user: 'User' = Relationship(back_populates="exercise_logs")
    exercise: 'Exercise' = Relationship(back_populates="exercise_logs")
    
class User(UserTableBase, table=True):
    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "select"})
    roles: list['Role'] = Relationship(back_populates="users", link_model=UserRoleLink, sa_relationship_kwargs={"lazy": "select"})
    exercises: list['Exercise'] = Relationship(back_populates="user")

class WorkoutExercise(WorkoutExerciseTableBase, table=True):
    workout: list['Workout'] = Relationship(back_populates="workout_exercises", link_model=WorkoutExerciseWorkoutOrderLink)

class Workout(WorkoutTableBase, table=True):
    workout_exercises: list['WorkoutExercise'] = Relationship(back_populates="workout", link_model=WorkoutExerciseWorkoutOrderLink)

class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True, unique_items=True)

    users: list['User'] = Relationship(back_populates="roles", link_model=UserRoleLink)



### Category Data
class WorkoutCategory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    exercises: list['Exercise'] = Relationship(back_populates="workout_category")

class MovementCategory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    exercises: list['Exercise'] = Relationship(back_populates="movement_category")

class MajorMuscle(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    exercises: list['Exercise'] = Relationship(back_populates="major_muscle")

class SpecificMuscle(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    
    exercises: list['Exercise'] = Relationship(back_populates="specific_muscles", link_model=ExerciseSpecificMuscleLink)

class Equipment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    band_color_id: int | None = Field(default=None, sa_column=Column(Integer, ForeignKey("bandcolor.id", ondelete="SET NULL"), index=True))
    
    exercises: list['Exercise'] = Relationship(back_populates="equipment")
    band_color: 'BandColor' = Relationship(back_populates="equipment")

class BandColor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    equipment: list['Equipment'] = Relationship(back_populates="band_color")