from sqlmodel import SQLModel, Field, create_engine
from models.models import ExerciseMuscleLink, Exercise, SingleWorkout, WorkoutPlanExerciseLink, WorkoutPlan, User

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///data/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
