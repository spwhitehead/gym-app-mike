from datetime import date
from typing import ClassVar
from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator, ConfigDict
from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, CHAR, Relationship

from models.utility import GUID, HashedPassword
from models.enums import Gender

from models.exercise_log import ExerciseLog
class UserBase(SQLModel):
    username: str = Field(unique=True)
    hashed_password: str = Field(sa_column=Column(HashedPassword())) 
    first_name: str
    last_name: str
    birthday: date
    body_weight: float
    height: int
    gender: Gender = Field(sa_column=Column(SQLEnum(Gender)))

    @field_validator("gender", mode="before", check_fields=False)
    def convert_str_to_resistance_type(cls, value: str) -> Gender:
        valid_values = ', '.join(gender.value for gender in Gender)
        if not isinstance(value, str):
            raise TypeError(f"resistance_type must be a string with a value of one of these items: {valid_values}")
        try:
            return Gender[value.upper()]
        except KeyError as e:
            raise ValueError(f"resistance_type must be one of: {valid_values}. Error: {str(e)}")

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID | None = Field(default_factory=new_uuid, sa_column=Column(GUID(), unique=True))

    exercise_logs: list['ExerciseLog'] = Relationship(back_populates="user")
    
    Config: ClassVar = ConfigDict(arbitrary_types_allowed=True, json_encoders= {HashedPassword: lambda v: str(v)})

class UserCreateReq(UserBase):
    pass
class UserUpdateReq(UserBase):
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    body_weight: float | None = None
    height: int | None = None
    gender: Gender | None = None

class UserResponseData(UserBase):
    uuid: UUID
    
class UserResponse(SQLModel):
    data: UserResponseData
    detail: str

class UserListResponse(SQLModel):
    data: list[UserResponseData]
    detail: str
