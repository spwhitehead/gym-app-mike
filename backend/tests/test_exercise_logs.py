from uuid import UUID
import json
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.relationship_merge import ExerciseLog, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor, Exercise, User

from db import get_db
from main import app

def build_database(engine):
    with open("exercise_json/new_exercise_json.json", 'r') as file:
        exercise_data: dict[str, object] = json.load(file)   
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
        band_colors: list[str] = ["yellow", "red", "green", "black", "purple", "blue", "orange", "gray"]
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
    client: TestClient = TestClient(app)

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

def test_empty_get_exercise_logs(client_full_db: TestClient):
    user_uuid: str = client_full_db.get("/users/").json()["data"][0]["uuid"]
    response: Response = client_full_db.get(f"/users/{user_uuid}/exercise_logs")
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 200
    assert response_dict == {
        "data": [],
        "detail": "Exercise Logs fetched successfully."
        }

def test_post_exercise_log(client_full_db: TestClient):
    user_uuid: str = client_full_db.get("/users").json()["data"][0]["uuid"]
    exercise_uuid: str = client_full_db.get("/exercises").json()["data"][0]["uuid"]
    exercise_log_data = {
        "datetime_completed": "2022-01-01T12:00:00",
        "exercise_uuid": exercise_uuid,
        "reps": 10,
        "weight": 145.0
        }
    response: Response = client_full_db.post(f"/users/{user_uuid}/exercise_logs", json=exercise_log_data)
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 201
    assert response_dict == {
        "data": {
            "datetime_completed": "2022-01-01T12:00:00",
            "user_uuid": user_uuid,
            "exercise": {
                "description": "Barbell Chest Press Description",
                "equipment": "Dumbbell",
                "major_muscle": "Chest",
                "movement_category": "Press",
                "name": "Barbell Chest Press",
                "specific_muscles": [
                    "Middle Chest",
                    "Triceps"
                    ],
                "uuid": exercise_uuid,
                "workout_category": "Upper"
                },
            "reps": 10,
            "uuid": response_dict["data"]["uuid"],
            "weight": 145.0
            },
        "detail": "Exercise log created successfully."
        }

def test_put_exercise_log(client_full_db: TestClient, session: Session):
    user_uuid: str = client_full_db.get("/users").json()["data"][0]["uuid"]
    exercise_uuid: str = client_full_db.get("/exercises").json()["data"][0]["uuid"]
    exercise_log_data: dict[str,object] = {
        "datetime_completed": "2022-01-01T12:00:00",
        "exercise_uuid": exercise_uuid,
        "reps": 10,
        "weight": 145.0
        }
    response: Response = client_full_db.post(f"/users/{user_uuid}/exercise_logs", json=exercise_log_data)
    response_dict: dict[str, object] = response.json() 
    response: Response = client_full_db.get(f"/users/{user_uuid}/exercise_logs")
    response_dict: dict[str, object] = response.json()
    exercise_log_uuid = response_dict["data"][0]["uuid"]
    exercise_uuid = client_full_db.get(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}").json()["data"]["exercise"]["uuid"]
    exercise_log_data = {
        "datetime_completed": "2025-01-01T12:00:00",
        "exercise_uuid": exercise_uuid,
        "reps": 200,
        "weight": 125.0
        }
    response: Response = client_full_db.put(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}", json=exercise_log_data)
    response_dict = response.json()
    exercise_log_uuid = UUID(exercise_log_uuid)
    exercise_log_uuid, exercise_id, user_id = map(str, session.exec(select(ExerciseLog.uuid, ExerciseLog.exercise_id, ExerciseLog.user_id).where(ExerciseLog.uuid == exercise_log_uuid)).first())
    assert response.status_code == 200
    assert response_dict == {
        "data": {
            "datetime_completed": "2025-01-01T12:00:00",
            "exercise": {
                "description": "Barbell Chest Press Description",
                "equipment": "Dumbbell",
                "major_muscle": "Chest",
                "movement_category": "Press",
                "name": "Barbell Chest Press",
                "specific_muscles": [
                    "Middle Chest",
                    "Triceps"
                    ],
                "uuid": exercise_uuid,
                "workout_category": "Upper"
                },
            "reps": 200,
            "uuid": exercise_log_uuid,
            "user_uuid": user_uuid,
            "weight": 125.0
            },
        "detail": "Exercise log updated successfully."
        }

def test_patch_exercise_log(client_full_db: TestClient, session: Session):
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    exercise_uuid = client_full_db.get("/exercises").json()["data"][0]["uuid"]
    exercise_log_data = {
        "datetime_completed": "2022-01-01T12:00:00",
        "exercise_uuid": exercise_uuid,
        "reps": 10,
        "weight": 145.0
        }
    response = client_full_db.post(f"/users/{user_uuid}/exercise_logs", json=exercise_log_data)
    response_dict = response.json()
    exercise_log_uuid = client_full_db.get(f"/users/{user_uuid}/exercise_logs").json()["data"][0]["uuid"]
    exercise_uuid = client_full_db.get(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}").json()["data"]["exercise"]["uuid"]
    exercise_log_data = {
        "reps": 20,
        "weight": 125.0
        }
    response: Response = client_full_db.patch(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}", json=exercise_log_data)
    response_dict = response.json()
    exercise_log_uuid = UUID(exercise_log_uuid)
    exercise_log_uuid, exercise_id, user_id = map(str, session.exec(select(ExerciseLog.uuid, ExerciseLog.exercise_id, ExerciseLog.user_id).where(ExerciseLog.uuid == exercise_log_uuid)).first())
    assert response.status_code == 200
    assert response_dict == {
        "data": {
            "datetime_completed": "2022-01-01T12:00:00",
            "exercise": {
                "description": "Barbell Chest Press Description",
                "equipment": "Dumbbell",
                "major_muscle": "Chest",
                "movement_category": "Press",
                "name": "Barbell Chest Press",
                "specific_muscles": [
                    "Middle Chest",
                    "Triceps"
                    ],
                "uuid": str(session.exec(select(Exercise).where(Exercise.id == exercise_id)).first().uuid),
                "workout_category": "Upper"
                },
            "reps": 20,
            "uuid": exercise_log_uuid,
            "user_uuid": str(session.exec(select(User).where(User.id == user_id)).first().uuid),
            "weight": 125.0
            },
        "detail": "Exercise log updated successfully."
        }

def test_delete_exercise(client_full_db: TestClient, session: Session):
    user_uuid = client_full_db.get("/users").json()["data"][0]["uuid"]
    exercise_uuid = client_full_db.get("/exercises").json()["data"][0]["uuid"]
    exercise_log_data = {
        "datetime_completed": "2022-01-01T12:00:00",
        "exercise_uuid": exercise_uuid,
        "reps": 10,
        "weight": 145.0
        }
    response: Response = client_full_db.post(f"/users/{user_uuid}/exercise_logs", json=exercise_log_data)
    exercise_log_uuid = client_full_db.get(f"/users/{user_uuid}/exercise_logs").json()["data"][0]["uuid"]
    assert session.exec(select(ExerciseLog).where(ExerciseLog.uuid == UUID(exercise_log_uuid))).first() != None
    response = client_full_db.delete(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}")
    assert response.status_code == 204
    assert session.exec(select(ExerciseLog).where(ExerciseLog.uuid == UUID(exercise_log_uuid))).first() == None
    response: Response = client_full_db.delete(f"/users/{user_uuid}/exercise_logs/{exercise_log_uuid}")
    response_dict = response.json()
    assert response.status_code == 404
    assert response_dict == {
        "detail": f"Exercise Log UUID: {exercise_log_uuid} not found."
        }