from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update


from db import engine

from models.exercise import Exercise, ExerciseMuscleLink
from models.requests import CreateExerciseRequest, UpdateExerciseRequest
from models.responses import ResponseExercise, ResponseExerciseList, ExerciseData

router = APIRouter()


# Exercises
@router.get("/exercises", response_model=ResponseExerciseList, status_code=status.HTTP_200_OK)
async def get_exercises() -> ResponseExerciseList:
    with Session(bind=engine) as session:
        exercises = session.exec(select(Exercise)).all()
        data = [ExerciseData(
            **exercise.model_dump(), 
            target_muscles=[muscle_link.musclegroup.value for muscle_link in exercise.target_muscles]
            ) for exercise in exercises]
        return ResponseExerciseList(data=data, detail="Exercises fetched successfully.")

@router.get("/exercises/{exercise_uuid}", response_model=ResponseExercise, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_uuid: UUID):
    with Session(bind=engine) as session:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise ID: {exercise_uuid} not found.")
        data = ExerciseData(**exercise.model_dump(), target_muscles=[muscle_link.musclegroup.value for muscle_link in exercise.target_muscles])
        return ResponseExercise(data=data, detail="Exercise fetched successfully.")

@router.post("/exercies/", response_model=ResponseExercise, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_request: CreateExerciseRequest) -> ResponseExercise:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        exercise = Exercise(uuid=uuid, **exercise_request.model_dump(exclude={"target_muscles"}))
        session.add(exercise)
        session.commit()
        session.refresh(exercise)
        print(exercise.id)
        for muscle_group in exercise_request.target_muscles:
            session.add(ExerciseMuscleLink(exercise_id=exercise.id, musclegroup=muscle_group.value))
        session.commit()
        session.refresh(exercise)
        data = ExerciseData(**exercise.model_dump(), target_muscles=[muscle_link.musclegroup.value for muscle_link in exercise.target_muscles])
        return ResponseExercise(data=data, detail=f"Exercise added successfully.")
            
        
