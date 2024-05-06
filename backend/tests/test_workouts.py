from uuid import UUID
import json
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.exercise import Exercise
from models.user import User
from models.unique_data import WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor
from models.exercise_log import ExerciseLog

from db import get_db
from main import app

def build_database(engine):
    with open("exercise_json/new_exercise_json.json", 'r') as file:
        exercise_data = json.load(file)   
    with Session(bind=engine) as session:
        for exercise in exercise_data:
            if not session.exec(select(WorkoutCategory).where(WorkoutCategory.name == exercise["workoutCategory"].title())).first():
                session.exec(insert(WorkoutCategory).values(name=exercise["workoutCategory"].title()))
            if not session.exec(select(MovementCategory).where(MovementCategory.name == exercise["movementCategory"].title())).first():
                session.exec(insert(MovementCategory).values(name=exercise["movementCategory"].title()))
            if not session.exec(select(MajorMuscle).where(MajorMuscle.name == exercise["majorMuscle"].title())).first():
                session.exec(insert(MajorMuscle).values(name=exercise["majorMuscle"].title()))
            for specific_muscle in exercise["specificMuscles"]:
                if not session.exec(select(SpecificMuscle).where(SpecificMuscle.name == specific_muscle.title())).first():
                    session.exec(insert(SpecificMuscle).values(name=specific_muscle.title()))
            if not session.exec(select(Equipment).where(Equipment.name == exercise["equipment"].title())).first():
                session.exec(insert(Equipment).values(name=exercise["equipment"].title()))
        band_colors = ["yellow", "red", "green", "black", "purple", "blue", "orange", "gray"]
        for color in band_colors:
            if not session.exec(select(BandColor).where(BandColor.name == color.title())).first():
                session.exec(insert(BandColor).values(name=color.title()))
        session.commit()
        return session
    

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return build_database(engine) 

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        return session
    
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)

    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="client_full_db")
def memory_client_fixture(client: TestClient):
    user_data = {
        "username": "programmerOne",
        "hashed_password": "programmer1",
        "first_name": "Wade",
        "last_name": "Watts",
        "birthday": "2020-05-03",
        "body_weight": 150,
        "height": 77,
        "gender": "male"
        }
    exercise_data = {
        "name": "Barbell Chest Press",
        "description": "Barbell Chest Press Description",
        "workout_category": "Upper",
        "movement_category": "Press",
        "equipment": "Dumbbell",
        "major_muscle": "Chest",
        "specific_muscles": [
            "Middle Chest", "Triceps"
            ]
        }
    
    client.post("/users", json=user_data)
    client.post("/exercises", json=exercise_data)
    yield client