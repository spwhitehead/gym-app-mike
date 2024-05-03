import json
from sqlmodel import SQLModel, create_engine, Session, select, insert
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event, inspect
from models.exercise import Exercise 
from models.exercise_specific_muscle_link import ExerciseSpecificMuscleLink
from models.workout_exercise import WorkoutExercise
from models.workout import Workout
from models.user import User
from models.exercise_log import ExerciseLog
from models.unique_data import WorkoutCategory, MovementCategory, BandColor, MajorMuscle, SpecificMuscle, Equipment

tables_list = ['exercisemajormusclelink','exercisespecificmusclelink','exercise','workoutexercise','workout','user','exerciselog','workoutcategory','movementcategory','bandcolor','majormusclegroup','specificmusclegroup','equipment']

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///data/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

inspector_engine = create_engine(sqlite_url, echo=False, isolation_level="AUTOCOMMIT")

def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

event.listen(engine, "connect", set_sqlite_pragma)

inspector = inspect(inspector_engine)

if not inspector.get_table_names():
    SQLModel.metadata.create_all(engine)
    with open("exercise_json/new_exercise_json.json", 'r') as file:
        exercise_data = json.load(file)   
    with Session(bind=engine) as session:
        for exercise in exercise_data:
            if not session.exec(select(WorkoutCategory).where(WorkoutCategory.name == exercise["workoutCategory"].title())).first():
                session.exec(insert(WorkoutCategory).values(name=exercise["workoutCategory"].title()))
            if not session.exec(select(MovementCategory).where(MovementCategory.name == exercise["movementCategory"].title())).first():
                session.exec(insert(MovementCategory).values(name=exercise["movementCategory"].title()))
            # if not session.exec(select(BandColor).where(BandColor.name == exercise["bandColor"])).first():
            #     session.exec(insert(BandColor).values(name=exercise["bandColor"].title()))
            if not session.exec(select(MajorMuscle).where(MajorMuscle.name == exercise["majorMuscle"].title())).first():
                session.exec(insert(MajorMuscle).values(name=exercise["majorMuscle"].title()))
            for specific_muscle in exercise["specificMuscles"]:
                if not session.exec(select(SpecificMuscle).where(SpecificMuscle.name == specific_muscle.title())).first():
                    session.exec(insert(SpecificMuscle).values(name=specific_muscle.title()))
            if not session.exec(select(Equipment).where(Equipment.name == exercise["equipment"].title())).first():
                session.exec(insert(Equipment).values(name=exercise["equipment"].title()))
        session.commit()

def get_db():
    with Session(bind=engine) as session:
        yield session

            