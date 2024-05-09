from typing import Any
from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.sqlite import VARCHAR

from bcrypt import hashpw, gensalt

class HashedPassword(TypeDecorator):
   
    impl = VARCHAR(60)
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        return dialect.type_descriptor(VARCHAR(60))
    
    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return value
        return hashpw(value.encode(), gensalt()).decode("utf-8")
    
    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        return value
    
    def __get_pydantic_core_schema__(self, handler):
        return {"type":"string"}