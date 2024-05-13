from uuid import UUID
from typing import Annotated
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlmodel import Session, select

from db import engine, get_db
from models.workout_exercise import WorkoutExerciseCreateReq, WorkoutExercisePatchReq
from models.responses import WorkoutExerciseResponseData, WorkoutExerciseResponse, WorkoutExerciseListResponse, ExerciseResponseData
from models.relationship_merge import WorkoutExercise, User, Exercise, WorkoutExerciseWorkoutOrderLink

from utilities.authorization import get_current_user, check_roles

router = APIRouter()

@lru_cache(maxsize=128)
def get_all_workout_exericses(current_user: User, session: Session):
    workout_exercises = session.exec(select(WorkoutExercise).where(WorkoutExercise.user_id == current_user.id)).all()
    data = []
    for workout_exercise in workout_exercises:
        exercise = session.exec(select(Exercise).where(Exercise.id == workout_exercise.exercise_id)).first()
        exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
        exercise_order = session.exec(select(WorkoutExerciseWorkoutOrderLink.exercise_order).where(WorkoutExerciseWorkoutOrderLink.workout_exercise_id == workout_exercise.id)).first()
        data.append(WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data, "exercise_order":exercise_order}))
    return data

def clear_workout_exercise_cache():
    get_all_workout_exericses.cache_clear()

#Workout Exercises End Points
@router.get("/users/me/workout-exercises", response_model=WorkoutExerciseListResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_workout_exercises(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> WorkoutExerciseListResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    data = get_all_workout_exericses(current_user, session)
    return WorkoutExerciseListResponse(data=data, detail=f"{len(data)} workout exercises fetched successfully." if len(data) != 1 else f"{len(data)} workout exercise fetched successfully.")

@router.get("/users/me/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_workout_exercise(current_user: Annotated[User, Security(get_current_user)], workout_exercise_uuid: UUID, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid).where(WorkoutExercise.user_id == current_user.id)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.id == workout_exercise.exercise_id)).first()
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    exercise_order = session.exec(select(WorkoutExerciseWorkoutOrderLink.exercise_order).where(WorkoutExerciseWorkoutOrderLink.workout_exercise_id == workout_exercise.id)).first()
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data, "exercise_order":exercise_order})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise fetched successfully.")

@router.post("/users/me/workout-exercises", response_model=WorkoutExerciseResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
@check_roles(["User"])
async def add_workout_exercise(current_user: Annotated[User, Security(get_current_user)], workout_exercise_request: WorkoutExerciseCreateReq, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    workout_exercise = WorkoutExercise.model_validate(workout_exercise_request.model_dump(), update={"user_id": current_user.id, "exercise_id": exercise.id})
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    session.refresh(exercise)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    exercise_order = session.exec(select(WorkoutExerciseWorkoutOrderLink.exercise_order).where(WorkoutExerciseWorkoutOrderLink.workout_exercise_id == workout_exercise.id)).first()
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise": exercise_data, "exercise_order":exercise_order})
    clear_workout_exercise_cache()
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise added successfully.")

@router.put("/users/me/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def update_workout_exercise(current_user: Annotated[User, Security(get_current_user)], workout_exercise_uuid: UUID, workout_exercise_request: WorkoutExerciseCreateReq, session: Session = Depends(get_db)):
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid).where(WorkoutExercise.user_id == current_user.id)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    for attr, value in workout_exercise_request.model_dump(exclude={"exercise_uuid"}).items():
        setattr(workout_exercise, attr, value)
    workout_exercise.exercise_id = exercise.id
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    exercise_order = session.exec(select(WorkoutExerciseWorkoutOrderLink.exercise_order).where(WorkoutExerciseWorkoutOrderLink.workout_exercise_id == workout_exercise.id)).first()
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data, "exercise_order":exercise_order})
    clear_workout_exercise_cache()
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise updated successfully.")

@router.patch("/users/me/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def update_workout_exercise(current_user: Annotated[User, Security(get_current_user)], workout_exercise_uuid: UUID, workout_exercise_request: WorkoutExercisePatchReq, session: Session = Depends(get_db)):
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid).where(WorkoutExercise.user_id == current_user.id)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    if workout_exercise_request.exercise_uuid:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise_request.exercise_uuid)).first() 
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    else:
        exercise = session.exec(select(Exercise).where(Exercise.id == workout_exercise.exercise_id)).first()
    for attr, value in workout_exercise_request.model_dump(exclude_unset=True, exclude={"exercise_uuid"}).items():
        setattr(workout_exercise, attr, value)
    if workout_exercise_request.exercise_uuid:
        workout_exercise.exercise_id = exercise.id
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    exercise_order = session.exec(select(WorkoutExerciseWorkoutOrderLink.exercise_order).where(WorkoutExerciseWorkoutOrderLink.workout_exercise_id == workout_exercise.id)).first()
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data, "exercise_order":exercise_order})
    clear_workout_exercise_cache()
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise updated successfully.")

@router.delete("/users/me/workout-exercises/{workout_exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"]) 
@check_roles(["User"])
async def delete_workout_exercise(current_user: Annotated[User, Security(get_current_user)], workout_exercise_uuid: UUID, session: Session = Depends(get_db)):
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid).where(WorkoutExercise.user_id == current_user.id)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    session.delete(workout_exercise)
    session.commit()
    clear_workout_exercise_cache()