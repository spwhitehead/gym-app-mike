from uuid import UUID

from sqlmodel import SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    user_uuid: UUID | None = None
    scopes: list[str] = []