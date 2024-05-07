from uuid import UUID
import json
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.relationship_merge import Workout, Exercise, ExerciseLog, User, WorkoutExercise, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor

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
    workout_data = {
        "name": "Chest Day",
        "description": "Chest Day Description"
    }
    
    client.post("/users", json=user_data)
    client.post("/exercises", json=exercise_data)
    user_uuid = client.get("/users").json()["data"][0]["uuid"]
    client.post(f"/users/{user_uuid}/workouts", json=workout_data)
    yield client

def test_get_empty_workouts(client: TestClient):
    client_data = {
        "username": "programmerOne",
        "hashed_password": "programmer1",
        "first_name": "Wade",
        "last_name": "Watts",
        "birthday": "2020-05-03",
        "body_weight": 150,
        "height": 70,
        "gender": "male"
    }
    client.post("/users", json=client_data)
    response: Response = client.get("/users")
    response_dict = response.json()
    user_uuid = response_dict["data"][0]["uuid"]
    response: Response = client.get(f"/users/{user_uuid}/workouts")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['data'] == []
    assert response_dict['detail'] == "0 workouts fetched successfully."

def test_get_workouts(client_full_db: TestClient):
    workout_data = {
        "name": "Back Day",
        "description": "Back Day Description"
        }
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    response = client_full_db.post(f"/users/{user_uuid}/workouts", json=workout_data)
    response_dict = response.json()
    response: Response = client_full_db.get(f"/users/{user_uuid}/workouts")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['data'] == [
        {
            "name": "Chest Day",
            "description": "Chest Day Description",
            "uuid": response_dict['data'][0]['uuid'],
            "workout_exercises": []
        },
        {
            "name": "Back Day",
            "description": "Back Day Description",
            "uuid": response_dict['data'][1]['uuid'],
            "workout_exercises": []
        }
    ]

def test_get_workout(client_full_db: TestClient):
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    workout_uuid = client_full_db.get(f"/users/{user_uuid}/workouts").json()["data"][0]["uuid"]
    response: Response = client_full_db.get(f"/users/{user_uuid}/workouts/{workout_uuid}")
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['data'] == {
        "name": "Chest Day",
        "description": "Chest Day Description",
        "uuid": workout_uuid,
        "workout_exercises": []
    }
    assert response_dict['detail'] == "Workout fetched successfully."

def test_post_workout(client_full_db: TestClient, session: Session):
    workout_data = {
        "name": "Leg Day",
        "description": "Leg Day Description"
        }
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    response: Response = client_full_db.post(f"/users/{user_uuid}/workouts", json=workout_data)
    response_dict = response.json()
    assert response.status_code == 201
    assert response_dict['data'] == {
        "name": "Leg Day",
        "description": "Leg Day Description",
        "uuid": response_dict['data']['uuid'],
        "workout_exercises": []
    }
    assert response_dict['detail'] == "Workout added successfully."
    assert session.exec(select(Workout).where(Workout.uuid == UUID(response_dict['data']['uuid']))).first().model_dump() == {
        "id": session.exec(select(Workout).where(Workout.uuid == UUID(response_dict['data']['uuid']))).first().id,
        "uuid": UUID(response_dict['data']['uuid']),
        "name": "Leg Day",
        "description": "Leg Day Description",
        "user_id": 1
    }

def test_put_workout(client_full_db: TestClient, session: Session):
    workout_data = {
        "name": "Leg Day",
        "description": "Leg Day Description"
        }
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    workout_uuid = client_full_db.post(f"/users/{user_uuid}/workouts", json=workout_data).json()["data"]["uuid"]
    response: Response = client_full_db.put(f"/users/{user_uuid}/workouts/{workout_uuid}", json=workout_data)
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['data'] == {
        "name": "Leg Day",
        "description": "Leg Day Description",
        "uuid": workout_uuid,
        "workout_exercises": []
    }
    assert response_dict['detail'] == "Workout updated successfully."
    assert session.exec(select(Workout).where(Workout.uuid == UUID(workout_uuid))).first().model_dump() == {
        "id": session.exec(select(Workout).where(Workout.uuid == UUID(workout_uuid))).first().id,
        "uuid": UUID(workout_uuid),
        "name": "Leg Day",
        "description": "Leg Day Description",
        "user_id": 1
    }

def test_patch_workout(client_full_db: TestClient, session: Session):
    workout_data = {
        "name": "Leg Day",
        "description": "Leg Day Description"
        }
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    workout_uuid = client_full_db.post(f"/users/{user_uuid}/workouts", json=workout_data).json()["data"]["uuid"]
    response: Response = client_full_db.patch(f"/users/{user_uuid}/workouts/{workout_uuid}", json={"name": "Arm Day"})
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['data'] == {
        "name": "Arm Day",
        "description": "Leg Day Description",
        "uuid": workout_uuid,
        "workout_exercises": []
    }
    assert response_dict['detail'] == "Workout updated successfully."
    assert session.exec(select(Workout).where(Workout.uuid == UUID(workout_uuid))).first().model_dump() == {
        "id": session.exec(select(Workout).where(Workout.uuid == UUID(workout_uuid))).first().id,
        "uuid": UUID(workout_uuid),
        "name": "Arm Day",
        "description": "Leg Day Description",
        "user_id": 1
    }

def test_delete_workout(client_full_db: TestClient, session: Session):
    workout_data = {
        "name": "Leg Day",
        "description": "Leg Day Description"
        }
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    workout_uuid = client_full_db.post(f"/users/{user_uuid}/workouts", json=workout_data).json()["data"]["uuid"]
    response: Response = client_full_db.delete(f"/users/{user_uuid}/workouts/{workout_uuid}")
    assert response.status_code == 204
    assert not session.exec(select(Workout).where(Workout.uuid == UUID(workout_uuid))).first()