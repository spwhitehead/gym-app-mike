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

def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
def setup_database(engine):
    if not inspect(engine).get_table_names():
        SQLModel.metadata.create_all(engine)
        populate_initial_data(engine)

def populate_initial_data(engine):
    with open("exercise_json/new_exercise_json.json", 'r') as file:
        exercise_data = json.load(file)
    with Session(engine) as session:
        # Bulk insert setup data if not exists
        for model, key in [(WorkoutCategory, "workoutCategory"), (MovementCategory, "movementCategory"), 
                           (MajorMuscle, "majorMuscle"), (Equipment, "equipment")]:
            existing_items = {item.name: item for item in session.exec(select(model))}
            new_items = set(exercise[key].title() for exercise in exercise_data)
            for item in new_items:
                if item not in existing_items:
                    session.add(model(name=item))
        for model, key in [(SpecificMuscle, "specificMuscles")]:
            existing_items = {item.name: item for item in session.exec(select(model))}
            new_items = set(specific_muscle.title() for exercise in exercise_data for specific_muscle in exercise[key])
            for item in new_items:
                if item not in existing_items:
                    session.add(model(name=item))
        
        band_colors = set(["Yellow", "Red", "Green", "Black", "Purple", "Green", "Orange", "Gray"])  # Use set for uniqueness
        existing_colors = {color.name for color in session.exec(select(BandColor))}
        session.add_all(BandColor(name=color) for color in band_colors if color not in existing_colors)
        
        session.commit()

# Engine setting and event listening setup
sqlite_url = "sqlite:///data/database.db"
engine = create_engine(sqlite_url, echo=False)
event.listen(engine, "connect", set_sqlite_pragma)

setup_database(engine)

with open("exercise_json/new_exercise_json.json", 'r') as file:
    exercise_data = json.load(file)
with Session(bind=engine) as session:
    for exercise in exercise_data:
        if session.exec(select(Exercise).where(Exercise.name == exercise["name"])).first():
            break
        name = exercise["name"]
        description = " ".join(exercise["description"])
        
        workout_category_name = exercise.get("workoutCategory", "").title()
        movement_category_name = exercise.get("movementCategory", "").title()
        major_muscle_name = exercise.get("majorMuscle", "").title()
        equipment_name = exercise.get("equipment", "").title()
        specific_muscles = exercise.get("specificMuscles", [])
        
        workout_category_id = session.exec(select(WorkoutCategory).where(WorkoutCategory.name == workout_category_name)).first().id
        movement_category_id = session.exec(select(MovementCategory).where(MovementCategory.name == movement_category_name)).first().id
        major_muscle_id = session.exec(select(MajorMuscle).where(MajorMuscle.name == major_muscle_name)).first().id
        equipment_id = session.exec(select(Equipment).where(Equipment.name == equipment_name)).first().id
        specific_muscles = [specific_muscle.title() for specific_muscle in specific_muscles]
        
        new_exercise = Exercise.model_validate({"name":name, "description":description, "workout_category_id":workout_category_id, "movement_category_id":movement_category_id, "major_muscle_id":major_muscle_id, "equipment_id":equipment_id})
        session.add(new_exercise)
        session.commit()
        session.refresh(new_exercise)
        for specific_muscle in specific_muscles:
            specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
            session.add(ExerciseSpecificMuscleLink(exercise_id=new_exercise.id, specific_muscle_id=specific_muscle_id))
        session.commit()


def get_db():
    with Session(bind=engine) as session:
        yield session

            