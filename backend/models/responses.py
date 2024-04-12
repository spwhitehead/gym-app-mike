from uuid import UUID 

from pydantic import BaseModel

from models.exercise import Exercise

class WorkoutPlanResponse(BaseModel):
    uuid: UUID
    name: str
    description: str
    exercises: list[Exercise] = []

class Response(BaseModel):
    data: WorkoutPlanResponse | list[WorkoutPlanResponse]
    detail: str





