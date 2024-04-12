from pydantic import BaseModel

class CreateWorkoutPlanRequest(BaseModel):
    name: str
    description: str

class UpdateWorkoutPlanRequest(BaseModel):
    name: str = None
    description: str = None