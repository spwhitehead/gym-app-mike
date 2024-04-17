from sqlmodel import SQLModel, create_engine
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event
from models.exercise import ExerciseMuscleLink, Exercise
from models.workout_exercise import WorkoutExercise
from models.workout import WorkoutExerciseLink, Workout
from models.user import User

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///data/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

event.listen(engine, "connect", set_sqlite_pragma)

SQLModel.metadata.create_all(engine)
