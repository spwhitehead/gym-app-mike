from datetime import date
from uuid import UUID
from uuid import uuid4 as new_uuid

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, CHAR

from models.utility import GUID
from models.enums import Gender

class UserBase(SQLModel):
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

    # @field_validator('uuid', mode="before", check_fields=False)
    # def convert_str_to_UUID(cls, value: str) -> UUID:
    #     if isinstance(value, str):
    #         try:
    #             return UUID(value)
    #         except ValueError as e:
    #             raise ValueError(f"UUID must be a valid UUID Str to convert to UUID. Value: {value} is of type {type(value)}, Error: {e}")
    #     else:
    #         return value
    
class UserResponse(SQLModel):
    data: UserResponseData
    detail: str

class UserListResponse(SQLModel):
    data: list[UserResponseData]
    detail: str