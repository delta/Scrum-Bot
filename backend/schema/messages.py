import logging
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Any, List, Optional, Union
from mongoengine import ObjectIdField, LazyReferenceField
from mongoengine.base.datastructures import LazyReference
from bson import ObjectId

from datetime import datetime

from schema.members import MemberInDBSchema, memberHelper
from schema.dbmodel import PyObjectId

from models.members import Member
from models.messages import Message


class CreateMessageSchema(BaseModel):
    """Message Schema"""

    messageId: str = Field(...)
    message: str = Field(...)
    tags: Optional[List[str]] = []
    isReply: bool = Field(False)
    replies = []
    author: str = Field(...)
    parentMessage: Optional[str]

    @validator("author")
    def checkIfAuthorContainsHash(cls, v):
        if not "#" in v:
            raise ValueError("Author name should contain a '#'")
        return v

    def checkIfValidMessage(self):
        """Check if the message follows correct format"""

        values = self.dict()
        isReply = self.isReply

        if isReply:
            # message is a reply, check if it follows the required format
            if "tags" in values and values["tags"] != []:
                # reply shouldn't contain tags
                return False, (
                    "A reply shouldn't contain tags. Check the data you have entered."
                )

            if (
                not "parentMessage" in values
                or "parentMessage" in values
                and values["parentMessage"] == None
            ):
                # a reply should have a parent message
                return False, (
                    "A reply should have a parent message. The given reply doesn't contain a parent message."
                )

        else:
            # the message is a discussion, check whether it has tags and return
            if not "tags" in values:
                return False, (
                    "A discussion should contain tags, the given message doesn't contain any tags."
                )
        return True, None

    @classmethod
    def getExample(self):
        examples = {
            "normalMessageSchema": {
                "summary": "Schema for a new Discussion",
                "description": "**Schema Explanation** for a new Discussion",
                "value": {
                    "messageId": "unique id of the message",
                    "message": "content of the message, length should be more then 20 characters",
                    "author": "discord handle of the user",
                    "tags": ["an", "array", "of", "all", "the", "tags"],
                },
            },
            "normalMessage": {
                "summary": "New Discussion Example",
                "description": "**Example** for a new Discussion body",
                "value": {
                    "messageId": "12334",
                    "message": "This is the message content",
                    "author": "joe#1234",
                    "tags": ["an", "array", "of", "all", "the", "tags"],
                },
            },
            "ReplySchema": {
                "summary": "Schema for a new Reply",
                "description": "**Schema Explanation** for a new Reply",
                "value": {
                    "messageId": "unique id of the message",
                    "message": "content of the reply, more than 20 characters long",
                    "author": "discord handle of the message author",
                    "isReply": True,
                    "parentMessage": "unique id of the message of the parent message ",
                },
            },
            "Reply": {
                "summary": "New Reply Example",
                "description": "**Example** for a new Reply body",
                "value": {
                    "messageId": "12335",
                    "message": "This is the content content of the reply",
                    "author": "joemama#1234",
                    "isReply": True,
                    "parentMessage": "12334",
                },
            },
        }
        return examples


class UpdateMessageSchema(BaseModel):
    """Update message schema"""

    messageId: str = Field(...)
    message: Optional[str] = None
    tags: Optional[List[str]] = None

    @classmethod
    def getExample(self):
        examples = {
            "schema": {
                "summary": "Schema for a update message",
                "description": "**Schema Explanation** for update message",
                "value": {
                    "messageId": "unique id of the message you want to edit",
                    "message": "Content of the message",
                    "tag": ["an", "array", "of", "all", "the", "tags"],
                },
            },
            "example_request": {
                "summary": "Update Message Example",
                "description": "**Example** for update message",
                "value": {
                    "messageId": "12334",
                    "message": "This is the edited message content",
                    "tags": ["an", "array", "of", "all", "the", "tags"],
                },
            },
        }
        return examples


class DeleteMessageSchema(BaseModel):
    """Delete message schema"""

    messageId: str = Field(...)

    @classmethod
    def getExample(self):
        examples = {
            "schema": {
                "summary": "Schema for a delete message",
                "description": "**Schema Explanation** for delete message",
                "value": {
                    "messageId": "unique id of the message you want to edit",
                },
            },
            "example_request": {
                "summary": "Delete Message Example",
                "description": "**Example** for delete message",
                "value": {
                    "messageId": "12334",
                },
            },
        }
        return examples


class MessageInDbSchema(BaseModel):
    messageId: Union[PyObjectId, str] = Field(...)
    mongoDocument: Optional[Any] = None

    message: str = Field(...)
    tags: Optional[List[str]]
    author: Union[Any, MemberInDBSchema]
    isDiscussion: bool = Field(True)
    replies: List["MessageInDbSchema"] = []
    parentMessage: Union["MessageInDbSchema", PyObjectId, str] = None

    timestamp: str = Field(...)

    def changeAuthorToPydanticSchema(self):
        try:
            assert isinstance(self.author, Member)
            self.author = MemberInDBSchema(**memberHelper(self.author))
            return
        except AssertionError as _:
            # author is already an instance of MemberInDBSchema, so just return
            return
        except Exception as e:
            logging.error(
                "Couldn't convert author to an instance of 'MemberInDBSchema' due to", e
            )
            raise Exception(
                "Couldn't convert author to an instance of 'MemberInDBSchema' due to", e
            )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#:~:text=data%20structures%20with%20self-referencing%20models%20are%20also%20supported%2C%20provided%20the%20function%20update_forward_refs()
MessageInDbSchema.update_forward_refs()

# API Response Models
class CreateMessageResponseModel(BaseModel):
    success: bool = Field(...)


class UpdateMessageResponseModel(CreateMessageResponseModel):
    pass


class DeleteMessageResponseModel(CreateMessageResponseModel):
    pass


class GetDiscussionsWithMatchingTagResponseModel(BaseModel):
    discussions: List[MessageInDbSchema]


class GetMessageWithMessageIdResponseModel(BaseModel):
    discussion: MessageInDbSchema


class GetDiscussionsPaginatedResponseModel(GetDiscussionsWithMatchingTagResponseModel):
    totalSize: Optional[int]


def messageHelper(message: Message):
    """Converts a single message document returned by a mongo to a dict"""
    time = datetime.strptime(str(message.timeStamp), "%Y-%m-%d %H:%M:%S.%f")

    messageDict = {
        "messageId": message.messageId,
        "message": message.message,
        "author": MemberInDBSchema(**memberHelper(message.author)),
        "timestamp": time.strftime("%b %d,%Y"),
        "replies": messageListHelper(message.replies),
        "mongoDocument": message,
    }

    messageDict["tags"] = message.tags

    if message.parentMessage:

        if not isinstance(message.parentMessage, LazyReference):
            messageDict["parentMessage"] = MessageInDbSchema(
                **messageHelper(message.parentMessage)
            )
        else:
            messageDict["parentMessage"] = message.parentMessage.pk
        messageDict["isDiscussion"] = False

    return messageDict


def messageListHelper(messages: List[Message]):
    """Converts a array of message document returned by a mongo to a list of MessageInDB pydantic obj"""

    if not messages or len(messages) == 0:
        return []

    return [MessageInDbSchema(**messageHelper(message)) for message in messages]
