from datetime import datetime
from typing import Any, Optional, Union
from mongoengine import ObjectIdField
from bson import ObjectId

from pydantic import BaseModel, Field


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(..., alias="updatedAt")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DBModelMixin(BaseModel):
    id: Optional[Union[PyObjectId, str]]
    objId: Optional[str] = None
    mongoDocument: Optional[Any]  # store the actual mongo document in this

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
