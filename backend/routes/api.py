from logging import error
from fastapi import FastAPI, APIRouter, Request, Response, Body
from datetime import datetime
from typing import Optional

from fastapi.param_functions import Depends

from controllers.scrum import (
    findAllScrums,
    findAllScrumsBetweenGivenInterval,
    findScrumWithGivenId,
)
from controllers.messages import (
    getAllDiscussionsByAnAuthor,
    getDiscussionsWithLimitAndOffset,
    getDiscussionsWithMatchingTags,
    getMessageWithMessageId,
)
from controllers.members import (
    getAllMembersFromDB,
    getMemberWithGivenId,
    updateMemberWithGivenDetails,
)
from schema.jwt import JWTToken

from schema.response import GenericResponseSchema
from schema.scrum import (
    GetAllScrumsBetweenGivenIntervalResponseModel,
    GetAllScrumsResponseModel,
    GetScrumWithGivenIdResponseModel,
)
from schema.messages import (
    GetDiscussionsPaginatedResponseModel,
    GetDiscussionsWithMatchingTagResponseModel,
    GetMessageWithMessageIdResponseModel,
)
from schema.members import (
    GetAllMembersResponseModel,
    GetMyUserModel,
    GetSingleMemberResponseModel,
    UpdateMemberSchema,
    UpdateMyUserModel,
)

from app.helper import ResponseModel, ErrorResponseModel
from app.utils import validateDateString
from app.auth import Authorization

router = APIRouter()
authHandler = Authorization(type="jwt")


@router.get(
    "/scrums",
    response_description="Gets all scrums",
    response_model=GenericResponseSchema[GetAllScrumsResponseModel],
)
def getAllScrums():
    """Finds all the scrums and returns an array of scrums"""
    resp = findAllScrums(excludeMessages=True, isParsed=True)
    if resp["statusCode"] == 200:
        return ResponseModel(data={"scrums": resp["data"]})
    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/scrums/",
    response_description="Gets all scrums between the given interval. Date should be of the format DD-MM-YYYY",
    response_model=GenericResponseSchema[GetAllScrumsBetweenGivenIntervalResponseModel],
)
def getAllScrumsInGivenInterval(
    start: str,
    end: str,
):
    """Finds all the scrums in the given interval.
    Both the dates(start and end) should be of the format **DD-MM-YYYY**."""
    ((startDate, endDate), errorMsg) = validateDateString(start, end)

    if errorMsg:
        return ErrorResponseModel(error={"error": errorMsg}, statuscode=400)

    resp = findAllScrumsBetweenGivenInterval(
        start=startDate, end=endDate, isParsed=True
    )
    if resp["statusCode"] == 200:
        return ResponseModel(data={"scrums": resp["data"]})
    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/scrums/{scrumId}",
    response_description="The scrum with the given id along with its disussions along with replies",
    response_model=GenericResponseSchema[GetScrumWithGivenIdResponseModel],
)
def getScrumWithGivenId(
    scrumId: str,
):
    """Finds the scrums with the given id and returns a the scrum details and
    all the **discussions** which occurred during that scrum."""

    resp = findScrumWithGivenId(scrumId=scrumId, isParsed=True)

    if [resp["statusCode"] == 200]:
        return ResponseModel(data={"scrum": resp["data"]}, message=resp["message"])

    if [resp["statusCode"] == 404]:
        return ErrorResponseModel(
            error=resp["error"], statuscode=404, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/discussions/find",
    response_description="A array of all the queried discussions",
    response_model=GenericResponseSchema[GetDiscussionsPaginatedResponseModel],
)
def getDiscussionsPaginated(
    limit: Optional[int] = None,
    offset: int = 0,
    author: Optional[str] = None,
):
    """Finds all the discussions with the given parameters and returns an array of messages.
    - The parameters can be either
        1. **Limit and offset** - Pagination
        2. **Author** - Gets all the discussions authored by the given user.
    - A request can contain limit and offest **or** author. **It cannot contain both.**"""
    resp = None

    if limit and not author:
        resp = getDiscussionsWithLimitAndOffset(
            limit=limit, offset=offset, isParsed=True
        )
    elif author and not limit:
        resp = getAllDiscussionsByAnAuthor(authorId=author, isParsed=True)

    if not resp:
        return ErrorResponseModel(
            statuscode=400,
            error="The provided parameters are incorrect. \
            The allowed parameters are \n 1. ?limit=Number&offset=Number \n 2. ?author=String",
            message="Bad request",
        )

    if resp["statusCode"] == 200:
        return ResponseModel(
            data={
                "discussions": resp["data"]["messages"],
                "totalSize": resp["data"]["totalSize"],
            },
            message=resp["message"],
        )

    if resp["statusCode"] == 404:
        return ErrorResponseModel(
            error=resp["error"], statuscode=404, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/discussions/search",
    response_description="A array of all the discussions with matching tag",
    response_model=GenericResponseSchema[GetDiscussionsWithMatchingTagResponseModel],
)
def getDiscussionsWithMatchingTag(
    tag: str,
):
    """Finds all the discussions which contains the tag query,
    and returns an array of found discussions
    ### NOTE : Since this is an expensive and long process, don't spam multiple requests to this end point"""

    resp = getDiscussionsWithMatchingTags(tag=tag, isParsed=True)

    if resp["statusCode"] == 200:
        return ResponseModel(
            data={"discussions": resp["data"]}, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/discussions/{discussionId}",
    response_description="Finds the discussion with the given discusssionId",
    response_model=GenericResponseSchema[GetMessageWithMessageIdResponseModel],
)
def getDiscussionWithDiscussionId(
    discussionId: str,
):
    """Finds the discussion **along with its replies** with the given discussionId"""
    resp = getMessageWithMessageId(messageId=discussionId, isParsed=True)

    if resp["statusCode"] == 200:
        return ResponseModel(data={"discussion": resp["data"]}, message=resp["message"])

    if [resp["statusCode"] == 404]:
        return ErrorResponseModel(
            error=resp["error"], statuscode=404, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/members",
    response_description="Returns an array of all the members along with their details",
    response_model=GenericResponseSchema[GetAllMembersResponseModel],
)
def getAllMembers():
    """Finds and returns an array of all the members along with their details."""
    resp = getAllMembersFromDB(isParsed=True)
    if resp["statusCode"] == 200:
        return ResponseModel(data={"members": resp["data"]}, message=resp["message"])

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/members/me",
    response_description="Returns the details of the user who is currently logged in.",
    response_model=GenericResponseSchema[GetSingleMemberResponseModel],
)
def getMe(user: JWTToken = Depends(authHandler.authenticateUser)):
    """Finds and returns the credentials of logged in user"""
    resp = getMemberWithGivenId(id=user.id, isParsed=True)
    if resp["statusCode"] == 200:
        return ResponseModel(data={"member": resp["data"]}, message=resp["message"])

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.put(
    "/members/me",
    response_description="Updates the current user's data (discordHandle, password, batch, name) with the provided data",
    response_model=GenericResponseSchema[UpdateMyUserModel],
)
def updateUserDetails(
    creds: UpdateMemberSchema = Body(...),
    user: JWTToken = Depends(authHandler.authenticateUser),
):
    """Updates the current user's details with the given details.
    **NOTE**: You cannot update the user's roll number with this route"""
    resp = updateMemberWithGivenDetails(data=creds, userId=user.id, isParsed=True)

    if resp["statusCode"] == 200:
        return ResponseModel(data={"member": resp["data"]}, message=resp["message"])

    if resp["statusCode"] == 400:
        ErrorResponseModel(
            error={"error": resp["error"]}, statuscode=400, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)


@router.get(
    "/members/{memberId}",
    response_description="Details of the user with the given userId",
    response_model=GenericResponseSchema[GetSingleMemberResponseModel],
)
def getSingleMember(
    memberId: str,
):
    """Finds the member with the given user id"""
    resp = getMemberWithGivenId(id=memberId, isParsed=True)

    if resp["statusCode"] == 200:
        return ResponseModel(data={"member": resp["data"]}, message=resp["message"])

    if [resp["statusCode"] == 404]:
        return ErrorResponseModel(
            error=resp["error"], statuscode=404, message=resp["message"]
        )

    return ErrorResponseModel(error={"error": resp["error"]}, statuscode=500)
