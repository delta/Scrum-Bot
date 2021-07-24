from fastapi import APIRouter, Body, Response, Request
from fastapi.encoders import jsonable_encoder
import logging

from app.helper import ResponseModel, ErrorResponseModel
from app.auth import Authorization

from controllers.constants import findCurrentScrum, setCurrentScrum
from controllers.scrum import createScrum, findScrumNameWithTheGivenId
from controllers.messages import (
    AddMessageToDataBase,
    UpdateMessageInDatabase,
    DeleteMessageInDatabase,
)

from schema.response import GenericResponseSchema
from schema.scrum import StartScrumResponse, EndScrumResponse, ScrumInDBSchema
from schema.messages import (
    CreateMessageSchema,
    CreateMessageResponseModel,
    UpdateMessageSchema,
    UpdateMessageResponseModel,
    DeleteMessageSchema,
    DeleteMessageResponseModel,
)

router = APIRouter()
botAuthHandler = Authorization(type="bot")


@router.get(
    "/scrum/start",
    response_description="Starts a scrum",
    response_model=GenericResponseSchema[StartScrumResponse],
)
def startScrum(request: Request):
    """Starts a scrum and returns scrumId and scrumName
    ## Requirements
    * There **should not** be another active scrum.
    * If there is an active scrum, it will throw a **400(Bad Request)** error"""
    # Check if a scrum is already active
    # if not start a scrum and update config table
    botAuthHandler.authenticateUser(request)
    try:
        scrum = findCurrentScrum()
        assert not scrum
        resp = createScrum()
        setCurrentScrum(scrumId=resp["data"]["scrumId"])
        return ResponseModel(data=resp["data"], message="A scrum has been started")

    except AssertionError as _:
        # a scrum is already going on, sending 400
        return ErrorResponseModel(
            message="A scrum is already active",
            error={"err": "A scrum with the id {} is already active".format(scrum)},
            statuscode=400,
        )

    except Exception as e:
        logging.error("Something went wrong, couldn't create a scrum", e)
        return ErrorResponseModel(
            message="Couldn't create a scrum, try again later",
            error={"error": e},
            statuscode=500,
        )


@router.get(
    "/scrum/end",
    response_description="Ends an active scrum",
    response_model=GenericResponseSchema[EndScrumResponse],
)
def endScrum(request: Request):
    """Ends the current active scrum and returns the scrum name
    ### **NOTE :** Don't forget to end the scrum after it's over."""
    # TODO: ? Maybe set a cron job for ending the scrum
    botAuthHandler.authenticateUser(request)
    try:
        scrum = findCurrentScrum()
        assert scrum
        resp = findScrumNameWithTheGivenId(scrum)

        # unset active scrum in constants collection
        setCurrentScrum()

        return ResponseModel(
            data=resp["data"], message="Ended {}".format(resp["data"]["scrumName"])
        )

    except AssertionError as _:
        return ErrorResponseModel(
            message="No scrum is active",
            error={"err": "No scrum is active to end"},
            statuscode=400,
        )
    except Exception as e:
        logging.error("Something went wrong, couldn't end scrum", e)

        return ErrorResponseModel(
            message="Couldn't end scrum, try again later",
            error={"error": e},
            statuscode=500,
        )


@router.post(
    "/message",
    response_description="Adds a message to the active scrum",
    response_model=GenericResponseSchema[CreateMessageResponseModel],
)
def addMessage(
    request: Request,
    message: CreateMessageSchema = Body(..., examples=CreateMessageSchema.getExample()),
):
    """Adds a messsage (Discussion / Reply) with the given data, and returns true or false
    * Only a discussion can contain tags array
    * Reply must have **isReply** set to true,
    * and a valid **Parent Message Id** as **parentMessage**"""
    # add message and send True or False

    botAuthHandler.authenticateUser(request)
    (isValid, error) = message.checkIfValidMessage()

    if not isValid:
        return ErrorResponseModel(error=error, statuscode=400, message="Bad Request")

    resp = AddMessageToDataBase(message=message, isParsed=True)

    return (
        ResponseModel(data={"success": resp["data"]}, message=resp["message"])
        if (resp["statusCode"] == 200)
        else ErrorResponseModel(
            message=resp["message"],
            error={"error": resp["error"]},
            statuscode=resp["statusCode"],
        )
    )


@router.put(
    "/message",
    response_description="Updates the message content and tags for the message with the given messageId",
    response_model=GenericResponseSchema[UpdateMessageResponseModel],
)
def updateMessage(
    request: Request,
    newMessage: UpdateMessageSchema = Body(
        ..., examples=UpdateMessageSchema.getExample()
    ),
):
    """Updates the the message with the given id, and sends whether it was successful. (true/false)"""
    # Update message and send True or False

    botAuthHandler.authenticateUser(request)
    resp = UpdateMessageInDatabase(message=newMessage, isParsed=True)

    return (
        ResponseModel(data={"success": resp["data"]}, message=resp["message"])
        if (resp["statusCode"] == 200)
        else ErrorResponseModel(
            message=resp["message"],
            error={"error": resp["error"]},
            statuscode=resp["statusCode"],
        )
    )


@router.delete(
    "/message",
    response_description="Deletes the message with the given messageId",
    response_model=GenericResponseSchema[DeleteMessageResponseModel],
)
def deleteMessage(
    request: Request,
    message: DeleteMessageSchema = Body(..., examples=DeleteMessageSchema.getExample()),
):
    """Deletes the message with the given id, and returns true or false"""

    botAuthHandler.authenticateUser(request)
    resp = DeleteMessageInDatabase(message=message, isParsed=True)

    return (
        ResponseModel(data={"success": resp["data"]}, message=resp["message"])
        if (resp["statusCode"] == 200)
        else ErrorResponseModel(
            message=resp["message"],
            error={"error": resp["error"]},
            statuscode=resp["statusCode"],
        )
    )
