from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine

from models.workout_plan import (
    WorkoutPlan
)

from models.requests import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest
)

from models.responses import (
    Response,
    WorkoutPlanResponse
)

router = APIRouter()


# Workout Plans
@router.get("/workout-plans", response_model=Response, status_code=status.HTTP_200_OK)
async def get_workout_plans() -> Response:
    with Session(bind=engine) as session:
        workout_plans = session.exec(select(WorkoutPlan)).all()
        data = [WorkoutPlanResponse(**workout_plan.model_dump()) for workout_plan in workout_plans]
        return Response(data=data, detail="Workout plans fetched successfully.")
    
@router.get("/workout-plans/{workout_plan_uuid}", response_model=Response, status_code=status.HTTP_200_OK)
async def get_workout_plan(workout_plan_uuid: UUID) -> Response:
    with Session(bind=engine) as session:
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.uuid == workout_plan_uuid)).first()
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Plan UUID: {workout_plan_uuid} not found.")
        data = WorkoutPlanResponse(**workout_plan.model_dump())
        return Response(data=data, detail="Workout plan fetched successfully.")

@router.post("/workout-plans/", response_model=Response, status_code=status.HTTP_201_CREATED)
async def add_workout_plan(workout_plan_request: CreateWorkoutPlanRequest) -> Response:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        session.exec(insert(WorkoutPlan).values(uuid=uuid, **workout_plan_request.model_dump()))
        session.commit()
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.uuid == uuid)).first()
        data = WorkoutPlanResponse(**workout_plan.model_dump())
        return Response(data=data, detail="Workout plan added successfully.")

@router.put("/workout-plans/{workout_plan_uuid}", response_model=Response, status_code=status.HTTP_200_OK)
async def update_workout_plan(workout_plan_uuid: UUID, workout_plan_request: UpdateWorkoutPlanRequest) -> Response:
    with Session(bind=engine) as session:
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.uuid == workout_plan_uuid)).first()
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout Plan UUID: {workout_plan_uuid} not found.")
        session.exec(update(WorkoutPlan).where(WorkoutPlan.uuid == workout_plan_uuid).values(
            name=workout_plan_request.name if workout_plan_request.name is not None else WorkoutPlan.name,
            description=workout_plan_request.name if workout_plan_request.name is not None else WorkoutPlan.name))
        session.commit() 
        session.refresh(workout_plan)
        data = WorkoutPlanResponse(**workout_plan.model_dump())
        return Response(data=data, detail="Workout Plan Updated.")

@router.delete("/workout-plans/{workout_plan_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_plan(workout_plan_uuid: UUID):
    with Session(bind=engine) as session:
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.uuid == workout_plan_uuid)).first()
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Plan UUID: {workout_plan_uuid} not found.")
        session.exec(delete(WorkoutPlan).where(WorkoutPlan.uuid == workout_plan_uuid))
        session.commit()