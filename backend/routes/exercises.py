
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, delete


from db import engine, get_db

from models.exercise import (
    Exercise,
    ExerciseMajorMuscleLink, ExerciseSpecificMuscleLink,
    ExerciseCreateReq, ExerciseUpdateReq,
    ExerciseResponse, ExerciseListResponse, ExerciseResponseData
)
from models.workout_exercise import WorkoutExercise

router = APIRouter()

# Exercises
@router.get("/exercises", response_model=ExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_exercises(session: Session = Depends(get_db)) -> ExerciseListResponse:
    exercises = session.exec(select(Exercise)).all()
    data = [ExerciseResponseData.model_validate(exercise) for exercise in exercises]
    return ExerciseListResponse(data=data, detail="Exercises fetched successfully.")

@router.get("/exercises/{exercise_uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_uuid: str, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise ID: {exercise_uuid} not found.")
    data = ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail="Exercise fetched successfully.")

@router.post("/exercises/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = Exercise.model_validate(exercise_request.model_dump())
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    for major_muscle in exercise_request.major_muscles:
        session.add(ExerciseMajorMuscleLink(major_muscle_group=major_muscle, exercise_id=exercise.id))
    for specific_muscle in exercise_request.specific_muscles:
        session.add(ExerciseSpecificMuscleLink(specific_muscle_group=specific_muscle, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.model_validate(exercise)

    return ExerciseResponse(data=data, detail=f"Exercise added successfully.")
            
@router.put("/exercises/{exercise_uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK) 
async def update_exercise(exercise_uuid: str, exercise_request: ExerciseUpdateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    for attr,value in exercise_request.model_dump(exclude_unset=True, exclude={"major_muscles", "specific_muscles"}).items():
        setattr(exercise, attr, value)
    print(exercise)
    print(exercise.major_muscles)
    print(exercise.specific_muscles)
    if exercise_request.major_muscles is not None:
        exercise.major_muscles.clear()
        for major_muscle in exercise_request.major_muscles:
            session.add(ExerciseMajorMuscleLink(major_muscle_group=major_muscle, exercise_id=exercise.id))
    if exercise_request.specific_muscles is not None:
        exercise.specific_muscles.clear()
        for specific_muscle in exercise_request.specific_muscles:
            session.add(ExerciseSpecificMuscleLink(specific_muscle_group=specific_muscle, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data =  ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise updated successfully.")

@router.delete("/exercises/{exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_uuid: str, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    session.exec(delete(WorkoutExercise).where(WorkoutExercise.exercise_uuid == exercise_uuid))
    session.exec(delete(Exercise).where(Exercise.uuid == exercise_uuid))
    session.commit()