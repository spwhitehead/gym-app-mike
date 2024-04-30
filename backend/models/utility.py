from typing import Any
from uuid import UUID
from sqlalchemy import Dialect
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.sqlite import VARCHAR

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses CHAR(32) as the database type for the GUID.
    """

    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        return dialect.type_descriptor(VARCHAR(32))
    
    def process_bind_param(self, value: Any | None, dialect: Dialect) -> str | None:
        print(value)
        print(type(value))
        if value is None:
            return value
        elif isinstance(value, UUID):
            return str(value)
        raise ValueError("Value needs to be a UUID instance.")
    
    def process_result_value(self, value: Any | None, dialect: Dialect) -> UUID | None:
        """Convert string from SQLite to Python UUID."""
        if value is None:
            return value
        return UUID(value)
