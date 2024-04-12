from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine, SQLModel

from models.models import (
    Exercise,
    SingleWorkout,
    WorkoutPlan,
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    User,
    ResistanceBand,
    MuscleGroup,
    BandColor,
    Gender,
    WeightUnits,
    HeightUnits,
    ResistenceType,
)

router = APIRouter()


# Workout Plans
@router.get("/workout-plans")
async def get_workout_plans():
    with Session(bind=engine) as session:
        workout_plans = session.exec(select(WorkoutPlan)).all()
        return workout_plans
    
@router.get("/workout-plans/{workout_plan_id}")
async def get_workout_plan(workout_plan_id: UUID):
    with Session(bind=engine) as session:
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.id == workout_plan_id)).first()
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Plan ID: {workout_plan_id} not found.")
        return workout_plan

@router.post("/workout-plans/")
async def add_workout_plan(workout_plan_request: CreateWorkoutPlanRequest):
    with Session(bind=engine) as session:
        workout_plan = session.exec(insert(WorkoutPlan).values(id=new_uuid(), **workout_plan_request.model_dump()))
        session.commit()
        session.refresh(workout_plan)
        return WorkoutPlan.create_response(**workout_plan.model_dump())

@router.put("/workout-plans/{workout_plan_id}")
async def update_workout_plan(workout_plan_id: UUID, workout_plan_request: UpdateWorkoutPlanRequest):
    with Session(bind=engine) as session:
        workout_plan = session.exec(update(WorkoutPlan).where(WorkoutPlan.id == workout_plan_id).values(
            name=workout_plan_request.name if workout_plan_request.name is not None else WorkoutPlan.name,
            description=workout_plan_request.name if workout_plan_request.name is not None else WorkoutPlan.name))
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout Plan ID: {workout_plan_id} not found.")
        session.commit() 
        session.refresh(workout_plan)
        return WorkoutPlan.update_response(**workout_plan.model_dump())

@router.delete("/workout-plans/{workout_plan_id}")
async def delete_workout_plan(workout_plan_id: UUID):
    with Session(bind=engine) as session:
        workout_plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.id == workout_plan_id)).first()
        if not workout_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Plan ID: {workout_plan_id} not found.")
        session.exec(delete(WorkoutPlan).where(WorkoutPlan.id == workout_plan_id))
        session.commit()
        return WorkoutPlan.delete_response(**workout_plan.model_dump()) 