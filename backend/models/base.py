# ==============================================================================
# File: base.py
# Project: Grocery Intelligence Platform
# Purpose: Shared Pydantic base models for MongDB 
# Author: Anita Woodford
# Created: 2024-06-01
# ==============================================================================

from __future__ import annotations # enables forwared reference hints
from datetime import UTC, datetime
from typing import Any, Generic, Optional, TypeVar # for generic type hinting

from bson import ObjectId # imports mongodbs object id type 
from pydantic import BaseModel, ConfigDict, Field # helpers
from pydantic_core import core_schema # for custom validation

T = TypeVar('T') # generic type variable for type hinting

def utc_now() -> datetime:
    """Returns the current UTC time with timezone information."""
    return datetime.now(UTC)

# define ObjectID type for pydantic models
class PyObjectId(ObjectId):
    
    @classmethod # makes the schema method a class level method
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
    # converts string value into an ObjectId, raises error if invalid
        def _validate(value):
            # Accept already-built ObjectId, str, or numeric-like input that can be str-cast
            if isinstance(value, ObjectId):
                return cls(str(value))
            if isinstance(value, str) and ObjectId.is_valid(value):
                return cls(value)
            raise ValueError("Invalid ObjectId")
        # Use a plain validator (single-arg) so pydantic core won't pass extra args
        return core_schema.no_info_plain_validator_function(
            _validate,
         serialization=core_schema.plain_serializer_function_ser_schema(str, when_used="json"),
        )
    
# define the shared base class for mongodb documents
class BaseDocument(BaseModel):
    # set shared pydantic behavior
    model_config = ConfigDict(
        populate_by_name=True, # allows population of fields by their name
        arbitrary_types_allowed=True, # allows for custom types like ObjectId
        extra="forbid", # forbids extra fields not defined in the model
        from_attributes=True, # allows population of fields from attributes
        validate_default=True, # validates default values
    )
    
    # store mondgoDB -Id while exposing it as id in python 
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    # store the document createion time
    created_at: datetime = Field(default_factory=utc_now)
    # store the last time updated timestamp
    updated_at: datetime = Field(default_factory=utc_now)



# define a reusable api response wrapper      
class StandardResponse(BaseModel, Generic[T]):
    # reject unexpected response fields
    model_config = ConfigDict(extra="forbid", validate_default=True)
    # store success response status
    success: bool
    # store optional response payload
    data: Optional[T] = None
    # Stores zero or more error messages without sharing one list across responses.    
    errors: list[str] = Field(default_factory=list)  
    # store optional response metadata
    meta: dict[str, Any] = Field(default_factory=dict)
    