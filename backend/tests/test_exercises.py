from uuid import UUID
from typing import Annotated
import json
import pytest
from pytest import MonkeyPatch
from pydantic import ValidationError
from jose import JWTError, jwt
from fastapi.testclient import TestClient
from fastapi.security import SecurityScopes
from fastapi import HTTPException, Depends, status
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.relationship_merge import Exercise, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor, User, Role
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event, inspect
import utilities.authorization
from utilities.authorization import get_current_user, oauth2_scheme, SECRET_KEY, ALGORITHM, TokenData, wraps
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
        roles = {"User", "Admin"}
        for role in roles:
            if not session.exec(select(Role).where(Role.name == role)).first():
                session.add(Role(name=role)) 
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
    
    def override_get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
        if security_scopes.scopes:
            authenticate_value = f"Bearer scope={security_scopes.scopes}"
        else:
            authenticate_value = "Bearer"
        credentials_exception = HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_uuid: UUID = UUID(payload.get("sub"))
            if user_uuid is None:
                raise credentials_exception
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(user_uuid=user_uuid, scopes=token_scopes)
        except (JWTError, ValidationError):
            raise credentials_exception
        user = session.exec(select(User).where(User.uuid == token_data.user_uuid)).first()
        if user is None:
            raise credentials_exception
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user
    
    
    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = override_get_current_user

    client = TestClient(app)

    registered_user = {
        "username": "user",
        "first_name": "user",
        "last_name": "user",
        "birthday": "2024-01-01",
        "body_weight": 100,
        "height": 70,
        "gender": "male",
        "hashed_password": "user",
        }

    client.post("/users/register", json=registered_user)
    
    login_data = {
        "username": "user",
        "password": "user"
    }
    
    response_dict = client.post("/users/login", data=login_data).json()

    client.headers['Authorization'] = f"Bearer {response_dict['access_token']}"

    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="client_full_db")
def memory_client_fixture(client: TestClient):
    data = [
        {
            "name": "Barbell Chest Press",
            "description": "Barbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Dumbbell",
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
    for exercise in data:
        client.post("/users/me/exercises", json=exercise)
    yield client
    

def test_get_empty_exercises(client: TestClient):
    response: Response = client.get("users/me/exercises")
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 200
    assert len(response_dict['data']) == 0
    assert response_dict['data'] == []

def test_get_exercises(client_full_db: TestClient, session: Session):
    response: Response = client_full_db.get("users/me/exercises")
    response_dict: dict[str, object] = response.json()
    for data in response_dict['data']:
        data['specific_muscles'].sort()
    response_dict['data'].sort(key=lambda x: x['name'])
    assert response.status_code == 200
    assert len(response_dict['data']) == 3
    assert response_dict == {
        'data': [
            {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][0]['uuid']))).first().uuid),
            "name": "Barbell Chest Press",
            "description": "Barbell Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Dumbbell",
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
        },
        {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][1]['uuid']))).first().uuid),
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
        {
            "uuid": str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][2]['uuid']))).first().uuid),
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
        ],
        'detail': 'Exercises fetched successfully.'
    }

def test_post_exercise(client: TestClient, session: Session):
    data = {
        "name": "Chest Press",
        "description": "Chest Press Description",
        "workout_category": "Upper",
        "movement_category": "Press",
        "equipment": "Dumbbell",
        "major_muscle": "Chest",
        "specific_muscles": [
            "Middle Chest", "Triceps"
        ]
    }
    response: Response = client.post("/users/me/exercises", json=data)
    response_dict = response.json()
    response_dict["data"]["specific_muscles"].sort()
    if 'detail' in response_dict:
        if 'msg' in response_dict['detail']:
            print(f"ERROR: {response_dict['detail']['msg']}")
    exercises = session.exec(select(Exercise).where(Exercise.name == response_dict["data"]["name"])).all()
    exercise_uuid = exercises[0].uuid
    assert response.status_code == 201
    expected_response = {
        "data": {
            "name": "Chest Press",
            "description": "Chest Press Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Dumbbell",
            "uuid": str(exercise_uuid),
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest",
                "Triceps"
            ]
            },
        "detail": "Exercise added successfully."
        }
    expected_response["data"]["specific_muscles"].sort()
    assert response_dict == expected_response

 
def test_update_exercise(client_full_db: TestClient, session: Session):
    response: Response = client_full_db.get("/users/me/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_uuid = str(response_dict["data"][0]["uuid"])
    new_data = {
            "name": "Dumbbell Chest Fly",
            "description": "Dumbbell Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Fly",
            "equipment": "Dumbbell",
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
            } 
    response = client_full_db.put(f"/users/me/exercises/{exercise_uuid}", json=new_data)
    response_dict = response.json()
    exercise_uuid = session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict["data"]["uuid"]))).first().uuid
    expected_response = {
        "data": {
            "uuid": str(exercise_uuid),
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
        "detail": "Exercise updated successfully."
        }
    response_dict["data"]["specific_muscles"].sort()
    expected_response["data"]["specific_muscles"].sort()
    assert response_dict == expected_response

def test_patch_exercise(client_full_db: TestClient, session: Session):
    response: Response = client_full_db.get("/users/me/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_uuid = str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][2]['uuid']))).first().uuid)
    new_data = {
            "name": "Dumbbell Incline Chest Fly",
            "description": "Dumbbell Incline Chest Fly Description",
            "major_muscle": "Chest"
            } 
    response = client_full_db.patch(f"/users/me/exercises/{exercise_uuid}", json=new_data)
    response_dict = response.json()
    for key, value in response_dict['data'].items():
        if isinstance(value, list):
            response_dict['data'][key].sort()
    expected_response = {
        "data": {
            "uuid": exercise_uuid,
            "name": "Dumbbell Incline Chest Fly",
            "description": "Dumbbell Incline Chest Fly Description",
            "workout_category": "Upper",
            "movement_category": "Press",
            "equipment": "Dumbbell",
            "major_muscle": "Chest",
            "specific_muscles": [
                "Middle Chest", "Triceps"
            ]
            },
        "detail": "Exercise patched successfully."
        }
    assert response.status_code == 200
    assert response_dict == expected_response 

def test_delete_exercise(client_full_db: TestClient, session: Session):
    response: Response = client_full_db.get("/users/me/exercises")
    response_dict: dict[str, object] = response.json()
    exercise_uuid: str = str(session.exec(select(Exercise).where(Exercise.uuid == UUID(response_dict['data'][1]['uuid']))).first().uuid)  
    response: Response = client_full_db.delete(f"/users/me/exercises/{exercise_uuid}")
    assert response.status_code == 204
