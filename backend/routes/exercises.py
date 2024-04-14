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

@router.post("/exercises/", response_model=ResponseExercise, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_request: CreateExerciseRequest) -> ResponseExercise:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        exercise = Exercise(uuid=uuid, **exercise_request.model_dump(exclude_unset=True, exclude={"target_muscles"}))
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
            
@router.put("/exercises/{exercise_uuid}", response_model=ResponseExercise, status_code=status.HTTP_200_OK) 
async def update_exercise(exercise_uuid: UUID, exercise_request: UpdateExerciseRequest) -> ResponseExercise:
    with Session(bind=engine) as session:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
        for key, value in exercise_request.model_dump(exclude_unset=True, exclude={"target_muscles"}).items():
            setattr(exercise, key, value)
        if exercise_request.target_muscles is not None:
            session.exec(delete(ExerciseMuscleLink).where(exercise.id == ExerciseMuscleLink.exercise_id))
            for muscle_group in exercise_request.target_muscles:
                session.add(ExerciseMuscleLink(exercise_id=exercise.id, musclegroup=muscle_group.value))
        session.commit()
        session.refresh(exercise)
        data = ExerciseData(**exercise.model_dump(), target_muscles=[muscle_link.musclegroup.value for muscle_link in exercise.target_muscles])
        return ResponseExercise(data=data, detail=f"Exercise updated successfully.")

@router.delete("/exercises/{exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_uuid: UUID):
    with Session(bind=engine) as session:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
        session.exec(delete(Exercise).where(Exercise.uuid == exercise_uuid))
        session.commit()