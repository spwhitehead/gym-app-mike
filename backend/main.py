from uuid import uuid4 as new_uuid
from uuid import UUID

from fastapi import FastAPI, HTTPException, status, APIRouter
from sqlmodel import Session, select, insert, delete

from db import engine, SQLModel
from routes import workout_plans, exercises

from models.exercise import (
    Exercise,
    SingleWorkout,
    ExerciseMuscleLink
)

from models.workout_plan import (
    WorkoutPlan,
    WorkoutPlanExerciseLink
    
)

from models.requests import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest
)

from models.responses import (
    Response,
    WorkoutPlanResponse
)

from models.user import (
    User
)

from models.resistance_band import (
    ResistanceBand
)

from models.enums import (
    BandColor,
    Gender,
    HeightUnits,
    MuscleGroup,
    ResistenceType,
    WeightUnits
)




app = FastAPI()
app.include_router(workout_plans.router) 
app.include_router(exercises.router)
