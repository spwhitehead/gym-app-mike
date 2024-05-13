
from uuid import UUID
from typing import Annotated
from functools import lru_cache
from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlmodel import Session, select, or_ 
from routes.authorization import get_current_user


from db import engine, get_db

from models.exercise import ExerciseCreateReq, ExercisePatchReq

from models.responses import ExerciseResponse, ExerciseListResponse, ExerciseResponseData

from models.relationship_merge import ExerciseSpecificMuscleLink, WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment, Exercise, User

from utilities.authorization import check_roles

router = APIRouter()

@lru_cache(maxsize=128)
def get_all_exercises_cached(current_user: User, session: Session) -> list[ExerciseResponseData]:
    exercises = session.exec(select(Exercise).where(or_(Exercise.user_id == current_user.id, Exercise.user_id == None))).all()
    data = [ExerciseResponseData.from_orm(exercise) for exercise in exercises]
    data.sort(key=lambda exercise: exercise.name)
    return data

@lru_cache(maxsize=128)
def get_user_created_exercises_cached(current_user: User, session: Session) -> list[ExerciseResponseData]:
    exercises = session.exec(select(Exercise).where(Exercise.user_id == current_user.id)).all()
    data = [ExerciseResponseData.from_orm(exercise) for exercise in exercises]
    data.sort(key=lambda exercise: exercise.name)
    return data

@lru_cache(maxsize=128)
def get_admin_created_exercises_cached(current_user: User, session: Session) -> list[ExerciseResponseData]:
    exercises = session.exec(select(Exercise).where(Exercise.user_id == None)).all()
    data = [ExerciseResponseData.from_orm(exercise) for exercise in exercises]
    data.sort(key=lambda exercise: exercise.name)
    return data
        
def get_specific_exercise_from_current_user(current_user: User, exercise_uuid: UUID, session: Session) -> Exercise:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    current_user_roles = [role.name for role in current_user.roles]
    if "User" in current_user_roles:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid).where(Exercise.user_id == current_user.id)).first()
    elif "Admin" in current_user_roles:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid).where(Exercise.user_id == None)).first()
    if not exercise:
        if session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User does not have permission to update Exercise UUID: {exercise_uuid}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    return exercise 

def verify_categories(workout_category_id: int, movement_category_id: int, major_muscle_id: int, equipment_id: int, exercise_post_request: ExerciseCreateReq, session: Session):
    if not workout_category_id:
        valid_options = session.exec(select(WorkoutCategory.name)).all()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout category '{exercise_post_request.workout_category}' is not a valid option. These are valid options: {valid_options}")
    if not movement_category_id:
        valid_options = session.exec(select(MovementCategory.name)).all()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movement category '{exercise_post_request.movement_category}' is not a valid option. These are valid options: {valid_options}")
    if not major_muscle_id:
        valid_options = session.exec(select(MajorMuscle.name)).all()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Major muscle '{exercise_post_request.major_muscle}' is not a valid option. These are valid options: {valid_options}")
    if not equipment_id:
        valid_options = session.exec(select(Equipment.name)).all()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Equipment '{exercise_post_request.equipment}' is not a valid option. These are valid options: {valid_options}")
    for specific_muscle in exercise_post_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        if not specific_muscle_id:
            valid_options = session.exec(select(SpecificMuscle.name)).all()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific Muscle '{specific_muscle}' is not a valid option. These are valid options: {valid_options}")

def clear_exercises_cache():
    get_all_exercises_cached.cache_clear()
    get_user_created_exercises_cached.cache_clear()
    get_admin_created_exercises_cached.cache_clear() 

# Exercises
@router.get("/users/me/exercises", response_model=ExerciseListResponse, status_code=status.HTTP_200_OK, tags=["Admin", "User"])
@check_roles(["User", "Admin"])
async def get_all_exercises(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db), user_created: bool = None, admin_created: bool = None) -> ExerciseListResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    if user_created and admin_created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot filter for both user and admin created exercises.")
    if not user_created and not admin_created:
        data = get_all_exercises_cached(current_user, session)
    if user_created:
        if "User" in [role.name for role in current_user.roles]:
            data = get_user_created_exercises_cached(current_user, session)
        elif "Admin" in [role.name for role in current_user.roles]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot view user created exercises.")
    if admin_created:
        data = get_admin_created_exercises_cached(current_user, session)
    return ExerciseListResponse(data=data, detail="Exercises fetched successfully.")

@router.get("/users/me/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK, tags=["Admin", "User"])
@check_roles(["User", "Admin"])
async def get_exercise(current_user: Annotated[User, Security(get_current_user)], exercise_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    data = ExerciseResponseData.from_orm(exercise)
    return ExerciseResponse(data=data, detail="Exercise fetched successfully.")


@router.post("/users/me/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED, tags=["Admin", "User"])
@check_roles(["User", "Admin"])
async def add_exercise(current_user: Annotated[User, Security(get_current_user)], exercise_post_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    workout_category_id = session.exec(select(WorkoutCategory.id).where(WorkoutCategory.name == exercise_post_request.workout_category)).first()
    movement_category_id = session.exec(select(MovementCategory.id).where(MovementCategory.name == exercise_post_request.movement_category)).first()
    major_muscle_id = session.exec(select(MajorMuscle.id).where(MajorMuscle.name == exercise_post_request.major_muscle)).first()
    equipment_id = session.exec(select(Equipment.id).where(Equipment.name == exercise_post_request.equipment)).first()
    verify_categories(workout_category_id, movement_category_id, major_muscle_id, equipment_id, exercise_post_request, session)
    current_user_roles = [role.name for role in current_user.roles]
    exercise = Exercise.model_validate(exercise_post_request.model_dump(
        exclude={"specific_muscles"}),
        update={"workout_category_id":workout_category_id,
                "movement_category_id": movement_category_id,
                "major_muscle_id": major_muscle_id,
                "equipment_id":equipment_id,
                "user_id":current_user.id if "User" in current_user_roles else None
                }
        )
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    for specific_muscle in exercise_post_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        session.add(ExerciseSpecificMuscleLink(exercise_id=exercise.id, specific_muscle_id=specific_muscle_id))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.from_orm(exercise)
    clear_exercises_cache()
    return ExerciseResponse(data=data, detail=f"Exercise added successfully.")
            

@router.put("/users/me/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK, tags=["Admin", "User"]) 
@check_roles(["User", "Admin"])
async def update_exercise(current_user: Annotated[User, Security(get_current_user)], exercise_uuid: UUID, exercise_put_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = get_specific_exercise_from_current_user(current_user, exercise_uuid, session)
    for attr,value in exercise_put_request.model_dump(exclude={"workout_category", "movement_category", "equipment", "major_muscle","specific_muscles"}).items():
        setattr(exercise, attr, value)
    workout_category_id = session.exec(select(WorkoutCategory.id).where(WorkoutCategory.name == exercise_put_request.workout_category)).first()
    movement_category_id = session.exec(select(MovementCategory.id).where(MovementCategory.name == exercise_put_request.movement_category)).first()
    major_muscle_id = session.exec(select(MajorMuscle.id).where(MajorMuscle.name == exercise_put_request.major_muscle)).first()
    equipment_id = session.exec(select(Equipment.id).where(Equipment.name == exercise_put_request.equipment)).first()
    verify_categories(workout_category_id, movement_category_id, major_muscle_id, equipment_id, exercise_put_request, session)
    exercise.workout_category_id = workout_category_id
    exercise.movement_category_id = movement_category_id
    exercise.major_muscle_id = major_muscle_id
    exercise.equipment_id = equipment_id
    for specific_muscle in exercise_put_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        if not specific_muscle_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific Muscle '{specific_muscle}' is not a valid option.")
    exercise.specific_muscles.clear()
    for specific_muscle in exercise_put_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        session.add(ExerciseSpecificMuscleLink(specific_muscle_id=specific_muscle_id, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data =  ExerciseResponseData.from_orm(exercise)
    clear_exercises_cache()
    return ExerciseResponse(data=data, detail=f"Exercise updated successfully.")

@router.patch("/users/me/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK, tags=["Admin", "User"])
@check_roles(["User", "Admin"])
async def update_exercise(current_user: Annotated[User, Security(get_current_user)], exercise_uuid: UUID, exercise_patch_request: ExercisePatchReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = get_specific_exercise_from_current_user(current_user, exercise_uuid, session)
    with session.no_autoflush:
        for attr, value in exercise_patch_request.model_dump(exclude_unset=True).items():
            match attr:
                case "name":
                    setattr(exercise, attr, value)
                case "description":
                    setattr(exercise, attr, value)
                case "workout_category":
                    workout_category_id = session.exec(select(WorkoutCategory).where(WorkoutCategory.name == value)).first().id
                    if not workout_category_id:
                        valid_options = session.exec(select(WorkoutCategory.name)).all()
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout category '{exercise_patch_request.workout_category}' is not a valid option. These are valid options: {valid_options}")
                    exercise.workout_category_id = workout_category_id
                case "movement_category":
                    movement_category_id = session.exec(select(MovementCategory).where(MovementCategory.name == value)).first().id
                    if not movement_category_id:
                        valid_options = session.exec(select(MovementCategory.name)).all()
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movement category '{exercise_patch_request.movement_category}' is not a valid option. These are valid options: {valid_options}")
                    exercise.movement_category_id = movement_category_id
                case "major_muscle":
                    major_muscle_id = session.exec(select(MajorMuscle).where(MajorMuscle.name == value)).first().id
                    if not major_muscle_id:
                        valid_options = session.exec(select(MajorMuscle.name)).all()
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Major muscle '{exercise_patch_request.major_muscle}' is not a valid option. These are valid options: {valid_options}")
                    exercise.major_muscle_id = major_muscle_id
                case "equipment":
                    equipment_id = session.exec(select(Equipment).where(Equipment.name == value)).first().id
                    if not equipment_id:
                        valid_options = session.exec(select(Equipment.name)).all()
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Equipment '{exercise_patch_request.equipment}' is not a valid option. These are valid options: {valid_options}")
                    exercise.equipment_id = equipment_id
                case "specific_muscles":
                    specific_muscle_objects = []
                    for specific_muscle in value:
                        specific_muscle_object = session.exec(select(SpecificMuscle).where(SpecificMuscle.name == value)).first()
                        if not specific_muscle_object:
                            valid_options = session.exec(select(SpecificMuscle.name)).all()
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific Muscle '{specific_muscle}' is not a valid option. These are valid options: {valid_options}")
                        specific_muscle_objects.append(specific_muscle_object)
                    exercise.specific_muscles.clear()
                    list(map(exercise.specific_muscles.append, specific_muscle_objects))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.from_orm(exercise)
    clear_exercises_cache()
    return ExerciseResponse(data=data, detail=f"Exercise patched successfully.")

@router.delete("/users/me/exercises/{exercise_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin", "User"])
@check_roles(["User", "Admin"])
async def delete_exercise(current_user: Annotated[User, Security(get_current_user)], exercise_uuid: UUID, session: Session = Depends(get_db)):
    exercise = get_specific_exercise_from_current_user(current_user, exercise_uuid, session)
    session.delete(exercise)
    session.commit()
    clear_exercises_cache()

