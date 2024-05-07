from uuid import UUID
import json
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.relationship_merge import Exercise, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor, User
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event, inspect


from db import get_db
from main import app


def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    event.listen(engine, "connect", set_sqlite_pragma)
    SQLModel.metadata.create_all(engine)
    return build_database(engine) 

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        return session
    
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    
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
    client.post("/users", json=user_data)
    
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="client_full_db")
def memory_client_fixture(client: TestClient, session: Session):
    exercise_data = [
        {
            "name": "Barbell Chest Press",
            "description": "Barbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Barbell",
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "name": "Dumbbell Chest Press",
            "description": "Dumbbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Dumbbell",
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "equipment": "Dumbbell",
            "major_muscle": "Chest", 
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
    ]
    for exercise in exercise_data:
        client.post("/exercises", json=exercise)
    workout_exercises_data = [
        {
            "planned_sets": 3,
            "planned_reps": 10,
            "planned_resistance_weight": 80,
            "exercise_uuid": str(session.exec(select(Exercise).where(Exercise.name == "Dumbbell Chest Press")).first().uuid)
        },
        {
            "planned_sets": 3,
            "planned_reps": 8,
            "planned_resistance_weight": 160,
            "exercise_uuid": str(session.exec(select(Exercise).where(Exercise.name == "Barbell Chest Press")).first().uuid)
        },
        {
            "planned_sets": 3,
            "planned_reps": 6,
            "planned_resistance_weight": 40,
            "exercise_uuid": str(session.exec(select(Exercise).where(Exercise.name == "Dumbbell Chest Fly")).first().uuid)
        }
        
    ] 
    user_uuid = session.exec(select(User).where(User.username == "programmerOne")).first().uuid
    for workout_exercise in workout_exercises_data:
        client.post(f"/users/{user_uuid}/workout-exercises", json=workout_exercise)
    
    yield client

def test_get_empty_workout_exercises(client: TestClient):
    response = client.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["data"] == []
    assert response_dict["detail"] == "0 workout exercises fetched successfully."

def test_get_workout_exercises(client_full_db: TestClient):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["data"] == [
        {
            'exercise': {
                'uuid': response_dict['data'][0]['exercise']['uuid'],
                'name': 'Dumbbell Chest Press',
                'description': 'Dumbbell Chest Press Description',
                'workout_category': 'Upper',
                'movement_category': 'Press',
                'equipment': 'Dumbbell',
                'major_muscle': 'Chest',
                'specific_muscles': ['Middle Chest', 'Triceps']
            },
            'uuid': response_dict['data'][0]['uuid'],
            'planned_sets': 3,
            'planned_reps': 10,
            'planned_resistance_weight': 80.0
        },
        {
            'exercise': {
                'uuid': response_dict['data'][1]['exercise']['uuid'],
                'name': 'Barbell Chest Press',
                'description': 'Barbell Chest Press Description',
                'workout_category': 'Upper',
                'movement_category': 'Press',
                'equipment': 'Barbell',
                'major_muscle': 'Chest',
                'specific_muscles': ['Middle Chest', 'Triceps']
            },
            'uuid': response_dict['data'][1]['uuid'],
            'planned_sets': 3,
            'planned_reps': 8,
            'planned_resistance_weight': 160.0
        },
        {
            'exercise': {
                'uuid': response_dict['data'][2]['exercise']['uuid'],
                'name': 'Dumbbell Chest Fly',
                'description': 'Dumbbell Chest Fly Description',
                'workout_category': 'Upper',
                'movement_category': 'Fly',
                'equipment': 'Dumbbell',
                'major_muscle': 'Chest',
                'specific_muscles': ['Middle Chest', 'Triceps']
            },
            'uuid': response_dict['data'][2]['uuid'],
            'planned_sets': 3,
            'planned_reps': 6,
            'planned_resistance_weight': 40.0
        },
    ]
    assert response_dict["detail"] == f"{len(response_dict['data'])} workout exercises fetched successfully."

def test_get_workout_exercise(client_full_db: TestClient):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    workout_exercise_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises/{workout_exercise_uuid}")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["data"] =={
            'exercise': {
                'uuid': response_dict['data']['exercise']['uuid'],
                'name': 'Dumbbell Chest Press',
                'description': 'Dumbbell Chest Press Description',
                'workout_category': 'Upper',
                'movement_category': 'Press',
                'equipment': 'Dumbbell',
                'major_muscle': 'Chest',
                'specific_muscles': ['Middle Chest', 'Triceps']
            },
            'uuid': response_dict['data']['uuid'],
            'planned_sets': 3,
            'planned_reps': 10,
            'planned_resistance_weight': 80.0
            }

def test_post_workout_exercise(client_full_db: TestClient, session: Session):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    workout_exercise_data = {
        "planned_sets": 3,
        "planned_reps": 8,
        "planned_resistance_weight": 30,
        "exercise_uuid": str(session.exec(select(Exercise).where(Exercise.name == "Dumbbell Chest Fly")).first().uuid)
    }
    response = client_full_db.post(f"/users/{user_uuid}/workout-exercises", json=workout_exercise_data)
    response_dict = response.json()
    assert response.status_code == 201
    assert response_dict["data"] == {
        'exercise': {
            'uuid': response_dict['data']['exercise']['uuid'],
            'name': 'Dumbbell Chest Fly',
            'description': 'Dumbbell Chest Fly Description',
            'workout_category': 'Upper',
            'movement_category': 'Fly',
            'equipment': 'Dumbbell',
            'major_muscle': 'Chest',
            'specific_muscles': ['Middle Chest', 'Triceps']
        },
        'uuid': response_dict['data']['uuid'],
        'planned_sets': 3,
        'planned_reps': 8,
        'planned_resistance_weight': 30.0
    }
    assert response_dict["detail"] == "Workout Exercise added successfully." 
    assert len(client_full_db.get(f"/users/{user_uuid}/workout-exercises").json()["data"]) == 4

def test_put_workout_exercise(client_full_db: TestClient, session: Session):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    workout_exercise_uuid = response_dict["data"][0]["uuid"]
    updated_workout_exercise_data = {
        "planned_sets": 3,
        "planned_reps": 8,
        "planned_resistance_weight": 30,
        "exercise_uuid": str(session.exec(select(Exercise).where(Exercise.name == "Dumbbell Chest Fly")).first().uuid)
    }
    response = client_full_db.put(f"/users/{user_uuid}/workout-exercises/{workout_exercise_uuid}", json=updated_workout_exercise_data)
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["data"] == {
        'exercise': {
            'uuid': response_dict['data']['exercise']['uuid'],
            'name': 'Dumbbell Chest Fly',
            'description': 'Dumbbell Chest Fly Description',
            'workout_category': 'Upper',
            'movement_category': 'Fly',
            'equipment': 'Dumbbell',
            'major_muscle': 'Chest',
            'specific_muscles': ['Middle Chest', 'Triceps']
        },
        'uuid': response_dict['data']['uuid'],
        'planned_sets': 3,
        'planned_reps': 8,
        'planned_resistance_weight': 30.0
    }
    assert response_dict["detail"] == "Workout Exercise updated successfully." 
    assert len(client_full_db.get(f"/users/{user_uuid}/workout-exercises").json()["data"]) == 3

def test_patch_workout_exercise(client_full_db: TestClient, session: Session):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    workout_exercise_uuid = response_dict["data"][0]["uuid"]
    updated_workout_exercise_data = {
        "planned_sets": 3,
        "planned_reps": 8
    }
    response = client_full_db.patch(f"/users/{user_uuid}/workout-exercises/{workout_exercise_uuid}", json=updated_workout_exercise_data)
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["data"] == {
        'exercise': {
            'uuid': response_dict['data']['exercise']['uuid'],
            'name': 'Dumbbell Chest Press',
            'description': 'Dumbbell Chest Press Description',
            'workout_category': 'Upper',
            'movement_category': 'Press',
            'equipment': 'Dumbbell',
            'major_muscle': 'Chest',
            'specific_muscles': ['Middle Chest', 'Triceps']
        },
        'uuid': response_dict['data']['uuid'],
        'planned_sets': 3,
        'planned_reps': 8,
        'planned_resistance_weight': 80.0
    }
    assert response_dict["detail"] == "Workout Exercise updated successfully." 
    assert len(client_full_db.get(f"/users/{user_uuid}/workout-exercises").json()["data"]) == 3

def test_delete_workout_exercise(client_full_db: TestClient):
    response = client_full_db.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.get(f"/users/{user_uuid}/workout-exercises")
    response_dict = response.json()
    workout_exercise_uuid = response_dict["data"][0]["uuid"]
    response = client_full_db.delete(f"/users/{user_uuid}/workout-exercises/{workout_exercise_uuid}")
    assert response.status_code == 204
    assert len(client_full_db.get(f"/users/{user_uuid}/workout-exercises").json()["data"]) == 2
    assert client_full_db.get(f"/users/{user_uuid}/workout-exercises/{workout_exercise_uuid}").status_code == 404