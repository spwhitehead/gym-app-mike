from uuid import uuid4 as new_uuid
from uuid import UUID 
from typing import Annotated 
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlmodel import Session, select, insert, delete, update 

from db import engine, get_db
from models.workout import (
    WorkoutCreateReq, WorkoutPatchReq, WorkoutAddWorkoutExerciseReq
)
from models.responses import (
    WorkoutResponseData, WorkoutResponse, WorkoutListResponse,
    ExerciseResponseData, WorkoutExerciseResponseData
)
from models.relationship_merge import (
    WorkoutExercise, Exercise, User, Workout
)

from utilities.authorization import get_current_user, check_roles

router = APIRouter()

@lru_cache(maxsize=1000)
def get_all_exercises_cached(current_user: User, session: Session) -> list[WorkoutResponseData]:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workouts = session.exec(select(Workout).where(Workout.user_id == current_user.id)).all()
    data = [WorkoutResponseData.model_validate(workout) for workout in workouts]
    data.sort(key=lambda workout: workout.name)
    return WorkoutListResponse(data=data, detail=f"{len(workouts)} workouts fetched successfully." if len(workouts) != 1 else f"{len(workouts)} workout fetched successfully.")

# Workout End Points
@router.get("/users/me/workouts", response_model=WorkoutListResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_workouts(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> WorkoutListResponse:
    return get_all_exercises_cached(current_user, session)
    
@router.get("/users/me/workouts/{workout_uuid:uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout fetched successfully.")

@router.post("/users/me/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
@check_roles(["User"])
async def create_workout(current_user: Annotated[User, Security(get_current_user)], workout_request: WorkoutCreateReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = Workout.model_validate(workout_request.model_dump(), update={"user_id": current_user.id})
    session.add(workout)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    get_all_exercises_cached.cache_clear()
    return WorkoutResponse(data=data, detail="Workout added successfully.")

@router.put("/users/me/workouts/{workout_uuid:uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def update_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, workout_request: WorkoutCreateReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
    for attr, value in workout_request.model_dump().items():
        setattr(workout, attr, value)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    get_all_exercises_cached.cache_clear()
    return WorkoutResponse(data=data, detail="Workout updated successfully.")

@router.patch("/users/me/workouts/{workout_uuid:uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def patch_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, workout_request: WorkoutPatchReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
    for attr, value in workout_request.model_dump(exclude_unset=True).items():
        setattr(workout, attr, value)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    get_all_exercises_cached.cache_clear()
    return WorkoutResponse(data=data, detail="Workout updated successfully.")

@router.delete("/users/me/workouts/{workout_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
@check_roles(["User"])
async def delete_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, session: Session = Depends(get_db)):
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    session.delete(workout)
    session.commit()
    get_all_exercises_cached.cache_clear()


# Workout Exercise End Points
@router.post("/users/me/workouts/{workout_uuid:uuid}/workout_exercises", response_model=WorkoutResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def link_workout_exercise_to_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, workout_add_workout_exercise_request: WorkoutAddWorkoutExerciseReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.") 
    workout_exercise = session.exec(select(WorkoutExercise) .where(WorkoutExercise.uuid == workout_add_workout_exercise_request.workout_exercise_uuid)).first()
    if not workout_exercise:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout Exercise UUID: {workout_uuid} not found.") 
    workout_exercise.exercise_order = len(workout.workout_exercises) + 1
    workout.workout_exercises.append(workout_exercise)
    session.commit()
    session.refresh(workout)
    session.refresh(workout_exercise)
    data = WorkoutResponseData.model_validate(workout)
    get_all_exercises_cached.cache_clear()
    return WorkoutResponse(data=data, detail="Added workout exercise succesfully.")

@router.patch("/users/me/workouts/{workout_uuid:uuid}/workout_exercises/{workout_exercise_uuid:uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def reorder_workout_exercise_in_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, workout_exercise_uuid: UUID, new_order: int, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_uuid} not found.")
    if new_order < 1 or new_order > len(workout.workout_exercises):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"New order must be between 1 and {len(workout.workout_exercises)}.")
    workout.workout_exercises.remove(workout_exercise)
    workout.workout_exercises.insert(new_order - 1, workout_exercise)
    session.commit()
    session.refresh(workout)
    for index, exercise in enumerate(workout.workout_exercises):
        exercise.exercise_order = index + 1
    session.commit()
    data = WorkoutResponseData.model_validate(workout)
    get_all_exercises_cached.cache_clear()
    return WorkoutResponse(data=data, detail="Workout exercise reordered successfully.")

@router.delete("/users/me/workouts/{workout_uuid:uuid}/workout_exercises/{workout_exercise_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
@check_roles(["User"])
async def unlink_workout_exercise_from_workout(current_user: Annotated[User, Security(get_current_user)], workout_uuid: UUID, workout_exercise_uuid: UUID, session: Session = Depends(get_db)):
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid).where(Workout.user_id == current_user.id)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_uuid} not found.")
    workout.workout_exercises.remove(workout_exercise)
    get_all_exercises_cached.cache_clear()
    session.commit()
    session.refresh(workout)
    for index, exercise in enumerate(workout.workout_exercises):
        exercise.exercise_order = index + 1
    session.commit()
    