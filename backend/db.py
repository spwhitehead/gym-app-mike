from sqlmodel import SQLModel, create_engine
from models.exercise import ExerciseMuscleLink, Exercise
from models.workout_exercise import WorkoutExercise
from models.workout import WorkoutExerciseLink, Workout
from models.user import User

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///data/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
