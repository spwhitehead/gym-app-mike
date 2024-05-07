from uuid import UUID
import json
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from db import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlmodel import select, insert
from models.relationship_merge import Exercise, User, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, BandColor

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
def memory_client_fixture(client: TestClient, session: Session):
    data = [
        {
            "username": "programmerOne",
            "hashed_password": "programmer1",
            "first_name": "Wade",
            "last_name": "Watts",
            "birthday": "2020-05-03",
            "body_weight": 150,
            "height": 77,
            "gender": "male"
        },
        {
            "username": "ZeroCool",
            "hashed_password": "hackers",
            "first_name": "Dade",
            "last_name": "Murphy",
            "birthday": "2020-05-03",
            "body_weight": 160,
            "height": 70,
            "gender": "male"
        },
        {
            "username": "MI",
            "hashed_password": "MI5",
            "first_name": "Ethan",
            "last_name": "Hunt",
            "birthday": "1985-05-03",
            "body_weight": 165,
            "height": 50,
            "gender": "male"
        }
    ]
    for user in data:
        response: Response = client.post("/users", json=user)
        response_json = response.json()
    clients = session.exec(select(User)).all()
    print(clients)
    yield client
    

def test_get_empty_users(client: TestClient, session: Session):
    response: Response = client.get("/users")
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 200
    assert response_dict == {
        'data': [],
        'detail': '0 users fetched successfully.',
        }

def test_get_users(client_full_db: TestClient, session: Session):
    users = session.exec(select(User)).all()
    response: Response = client_full_db.get("/users")
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 200
    assert response_dict['detail'] == "3 users fetched successfully."
    assert len(response_dict['data']) == 3
    assert response_dict == {
        'data': [
            {
                "username": "programmerOne",
                "hashed_password": f"{session.exec(select(User).where(User.username == "programmerOne")).first().hashed_password}",
                "first_name": "Wade",
                "last_name": "Watts",
                "birthday": "2020-05-03",
                "body_weight": 150.0,
                "height": 77,
                "gender": "male",
                "uuid": f"{session.exec(select(User).where(User.username == "programmerOne")).first().uuid}"
                },
                {
                "username": "ZeroCool",
                "hashed_password": f"{session.exec(select(User).where(User.username == "ZeroCool")).first().hashed_password}",
                "first_name": "Dade",
                "last_name": "Murphy",
                "birthday": "2020-05-03",
                "body_weight": 160.0,
                "height": 70,
                "gender": "male",
                "uuid": f"{session.exec(select(User).where(User.username == "ZeroCool")).first().uuid}"
                },
                {
                "username": "MI",
                "hashed_password": f"{session.exec(select(User).where(User.username == "MI")).first().hashed_password}",
                "first_name": "Ethan",
                "last_name": "Hunt",
                "birthday": "1985-05-03",
                "body_weight": 165.0,
                "height": 50,
                "gender": "male",
                "uuid": f"{session.exec(select(User).where(User.username == "MI")).first().uuid}"
                }
            ],
        'detail': '3 users fetched successfully.'
    }

def test_post_user(client: TestClient, session: Session):
    data = {
        "username": "programmerOne",
        "hashed_password": "programmer1",
        "first_name": "Wade",
        "last_name": "Watts",
        "birthday": "2020-05-03",
        "body_weight": 150,
        "height": 77,
        "gender": "male"
    }
    response: Response = client.post("/users", json=data)
    response_dict: dict[str, object] = response.json()
    assert response.status_code == 201
    assert len(session.exec(select(User)).all()) == 1
    assert response_dict == {
        'data':{
                "username": "programmerOne",
                "hashed_password": f"{session.exec(select(User).where(User.username == 'programmerOne')).first().hashed_password}",
                "first_name": "Wade",
                "last_name": "Watts",
                "birthday": "2020-05-03",
                "body_weight": 150.0,
                "height": 77,
                "gender": "male",
                "uuid": f"{session.exec(select(User).where(User.username == 'programmerOne')).first().uuid}"
                },
        'detail': 'New User has been added.'
        }

def test_put_user(client_full_db: TestClient, session: Session):
    data = {
        "username": "programmerOne",
        "hashed_password": "programmer1",
        "first_name": "Wade",
        "last_name": "Watts",
        "birthday": "2020-05-03",
        "body_weight": 100,
        "height": 70,
        "gender": "female"
    }
    user = session.exec(select(User).where(User.username == 'programmerOne')).first()
    user_uuid = user.uuid
    response: Response = client_full_db.put(f"/users/{user_uuid}", json=data)
    response_dict: dict[str, object] = response.json()
    session.refresh(user)
    hashed_password = user.hashed_password
    assert response.status_code == 200
    assert response_dict == {
        'data':{
                "username": "programmerOne",
                "hashed_password": f"{session.exec(select(User).where(User.username == 'programmerOne')).first().hashed_password}",
                "first_name": "Wade",
                "last_name": "Watts",
                "birthday": "2020-05-03",
                "body_weight": 100.0,
                "height": 70,
                "gender": "female",
                "uuid": f"{session.exec(select(User).where(User.username == 'programmerOne')).first().uuid}"
                },
        'detail': 'User updated.'
    }
    assert user.username == "programmerOne"
    assert user.hashed_password == hashed_password
    assert user.first_name == "Wade"
    assert user.last_name == "Watts"
    assert user.birthday.isoformat() == "2020-05-03"
    assert user.body_weight == 100.0
    assert user.height == 70
    assert user.gender == "female"
    assert user.uuid == user_uuid

def test_patch_user(client_full_db: TestClient, session: Session):
    data = {
        "body_weight": 200,
        "height": 80
    }
    user = session.exec(select(User).where(User.username == 'programmerOne')).first()
    user_uuid = user.uuid
    response: Response = client_full_db.patch(f"/users/{user_uuid}", json=data)
    response_dict: dict[str, object] = response.json()
    session.refresh(user)
    hashed_password = user.hashed_password
    assert response.status_code == 200
    assert response_dict == {
        'data':{
                "username": "programmerOne",
                "hashed_password": hashed_password,
                "first_name": "Wade",
                "last_name": "Watts",
                "birthday": "2020-05-03",
                "body_weight": 200.0,
                "height": 80,
                "gender":"male",
                "uuid": str(user.uuid),
                },
        'detail': 'User updated.'
    }

def test_delete_user(client_full_db: TestClient, session: Session):
    user = session.exec(select(User).where(User.username == 'programmerOne')).first()
    user_uuid = user.uuid
    response: Response = client_full_db.delete(f"/users/{user_uuid}")
    assert response.status_code == 204
    assert len(session.exec(select(User)).all()) == 2
    assert not session.exec(select(User).where(User.username == 'programmerOne')).first()
    assert session.exec(select(User).where(User.username == 'ZeroCool')).first()
    assert session.exec(select(User).where(User.username == 'MI')).first()