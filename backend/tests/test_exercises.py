from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from fastapi import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select
from models.exercise import Exercise

from db import get_db
from main import app

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        return session
    
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="client_db")
def database_fixture(client: TestClient):
    data = [
        {
            "name": "Barbell Chest Press",
            "description": "Barbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest", "Arms"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "name": "Dumbbell Chest Press",
            "description": "Dumbbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest", "Arms"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
    ]
    
    for exercise in data:
        client.post("/exercises", json=exercise)
    yield client
    

def test_get_empty_exercises(client: TestClient):
    response: Response = client.get("/exercises")
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 200
    assert response_dict == {
        'data': [],
        'detail': 'Exercises fetched successfully.',
        }

def test_get_exercises(client_db: TestClient, session: Session):
    response: Response = client_db.get("exercises")
    response_dict: dict[str, object] = response.json()
    for data in response_dict['data']:
        data['major_muscles'].sort()
        data['specific_muscles'].sort()
    assert response.status_code == 200
    assert response_dict == {
        'data': [
            {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][0]['uuid']))).first().uuid),
            "name": "Barbell Chest Press",
            "description": "Barbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Arms", "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][1]['uuid']))).first().uuid),
            "name": "Dumbbell Chest Press",
            "description": "Dumbbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Arms", "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][2]['uuid']))).first().uuid),
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        ],
        'detail': 'Exercises fetched successfully.'
    }

def test_post_exercise(client: TestClient, session: Session):
    data = {
        "name": "Chest Press",
        "description": "Chest Press Description",
        "workout_category": "Upper",
        "movement_category": "Press",
        "resistance_type": "Dumbbell",
        "major_muscles": [
            "Chest"
        ],
        "specific_muscles": [
            "Middle Chest", "Triceps"
        ]
    }
    response: Response = client.post("/exercises", json=data)
    response_dict = response.json()
    response_dict["data"]["major_muscles"].sort()
    response_dict["data"]["specific_muscles"].sort()
    if 'detail' in response_dict:
        if 'msg' in response_dict['detail']:
            print(f"ERROR: {response_dict['detail']['msg']}")
    exercises = session.exec(select(Exercise).where(Exercise.name == response_dict["data"]["name"])).all()
    exercise_uuid = exercises[0].uuid
    print(exercise_uuid)
    assert response.status_code == 201
    expected_response = {
        "data": {
            "name": "Chest Press",
            "description": "Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "resistance_type": "Dumbbell",
            "uuid": str(exercise_uuid),
            "major_muscles": [
                "Chest"
            ],
            "specific_muscles": [
                "Middle Chest",
                "Triceps"
            ]
            },
        "detail": "Exercise added successfully."
        }
    expected_response["data"]["major_muscles"].sort()
    expected_response["data"]["specific_muscles"].sort()
    assert response_dict == expected_response

    
def test_update_exercise(client_db: TestClient, session: Session):
    response: Response = client_db.get("/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_id = str(response_dict["data"][0]["uuid"])
    new_data = {
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
            } 
    response = client_db.put(f"/exercises/{exercise_id}", json=new_data)
    response_dict = response.json()
    exercise_uuid = session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict["data"]["uuid"]))).first().uuid
    expected_response = {
        "data": {
            "uuid": str(exercise_uuid),
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
            },
        "detail": "Exercise updated successfully."
        }
    response_dict["data"]["major_muscles"].sort()
    response_dict["data"]["specific_muscles"].sort()
    expected_response["data"]["major_muscles"].sort()
    expected_response["data"]["specific_muscles"].sort()
    assert response_dict == expected_response

def test_patch_exercise(client_db: TestClient, session: Session):
    response: Response = client_db.get("/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_uuid = str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][2]['uuid']))).first().uuid)
    new_data = {
            "name": "Dumbbell Incline Chest Fly",
            "description": "Dumbbell Incline Chest Fly Description",
            "major_muscles": [
                "Chest", "Arms"
            ],
            } 
    response = client_db.patch(f"/exercises/{exercise_uuid}", json=new_data)
    response_dict = response.json()
    response_dict['data']['major_muscles']
    for key, value in response_dict['data'].items():
        if isinstance(value, list):
            response_dict['data'][key].sort()
    expected_response = {
        "data": {
            "uuid": exercise_uuid,
            "name": "Dumbbell Incline Chest Fly",
            "description": "Dumbbell Incline Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "resistance_type": "Dumbbell",
            "major_muscles": [
                "Arms", "Chest"
            ],
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
            },
        "detail": "Exercise patched successfully."
        }
    assert response.status_code == 200
    assert response_dict == expected_response 

def test_delete_exercise(client_db: TestClient, session: Session):
    response: Response = client_db.get("/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_uuid: str = str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][1]['uuid']))).first().uuid)  
    response: Response = client_db.delete(f"/exercises/{exercise_uuid}")
    assert response.status_code == 204