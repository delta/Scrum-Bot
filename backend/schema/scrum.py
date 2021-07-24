from pydantic import BaseModel, Field
from typing import Any, List
from datetime import datetime

from models.scrum import Scrum

from schema.dbmodel import DBModelMixin
from schema.messages import messageListHelper


class ScrumInDBSchema(DBModelMixin):
    name: str = Field(...)
    created_at: str = Field(...)
    messages: List[Any]


# API Response Models
class StartScrumResponse(BaseModel):
    scrumId: str = Field(...)
    scrumName: str = Field(...)


class EndScrumResponse(BaseModel):
    scrumName: str = Field(...)


class GetAllScrumsResponseModel(BaseModel):
    scrums: List[ScrumInDBSchema]


class GetAllScrumsBetweenGivenIntervalResponseModel(GetAllScrumsResponseModel):
    pass


class GetScrumWithGivenIdResponseModel(BaseModel):
    scrum: ScrumInDBSchema


def scrumHelper(scrum: Scrum):
    """Converts a single scrum document returned by a mongo to a dict"""
    time = datetime.strptime(str(scrum.created_at), "%Y-%m-%d %H:%M:%S.%f")
    print(scrum.messages)
    return {
        "id": scrum.id,
        "objId": str(scrum.id),
        "mongoDocument": scrum,
        "name": scrum.name,
        "created_at": time.strftime("%d %b %Y"),
        "messages": messageListHelper(scrum.messages),
    }
