import logging
from datetime import datetime
from typing import List

from models.scrum import Scrum
from models.messages import Message

from app.helper import parseControllerResponse

from controllers.constants import findCurrentScrum

from schema.scrum import ScrumInDBSchema, scrumHelper
from schema.messages import messageListHelper


def createScrum():
    """Creates a scrum and returns the its object id"""

    # * Note: make sure to check there is no active scrum,
    #         before calling create scrum
    #
    # * Also need to set active scrum to the created scrum id

    try:
        newScrum = Scrum()
        newScrum.name = newScrum.generateName()
        newScrum.messages = []
        newScrum.save()
        resp = {"scrumId": newScrum.id.__str__(), "scrumName": newScrum.name}

        return parseControllerResponse(
            data=resp, statuscode=200, message="Scrum Created"
        )

    except Exception as e:
        logging.error("Couldn't create a scrum due to ", e)
        raise Exception("Couldn't create a scrum due to ", e)


def findScrumNameWithTheGivenId(id: str):
    """Finds the scrum with the given id and returns its name"""

    try:
        scrum = Scrum.objects(id=id).first()

        resp = {"scrumName": scrum.name}

        return parseControllerResponse(resp, statuscode=200, message="Scrum Found")

    except Exception as e:
        logging.error("Couldn't find the scrum with the id : {}. Due to".format(id), e)
        raise Exception(
            "Couldn't find the scrum with the id : {}. Due to".format(id), e
        )


def addMessageToScrum(message: Message):
    """Adds a a message to the current scrum"""

    try:
        currentScrumId = findCurrentScrum()

        # make sure a scrum exists
        #
        # this only raises an Exception (instead of HTTPException),
        # it will be easier to handle somewhere else
        assert currentScrumId

        scrum: Scrum = Scrum.objects(id=currentScrumId).first()
        scrum.messages.append(message)

        scrum.save()

        return
    except AssertionError as _:
        # caused due to improper calling of this function
        # Handling this error just in case
        raise Exception("No active scrum to add a message")
    except Exception as e:
        logging.error("Couldn't add message to the scrum due to {}".format(e))
        raise Exception("Couldn't add message to the scrum due to {}".format(e))


def findAllScrums(**kwargs):
    """Finds all the scrums"""
    excludeMessages = kwargs.get("excludeMessages", False)
    isResponseParsed = kwargs.get("isParsed", False)

    try:
        rawScrums = (
            Scrum.objects()
            if not excludeMessages
            else Scrum.objects().fields(messages=0)
        )  # don't include messages

        scrums = [ScrumInDBSchema(**scrumHelper(rawScrum)) for rawScrum in rawScrums]

        if not isResponseParsed:
            return scrums

        # convert the pydantic obj to a array of dict
        resp = [scrum.dict(exclude={"mongoDocument"}) for scrum in scrums]

        return parseControllerResponse(data=resp, statuscode=200)

    except Exception as e:
        errorMsg = "Couldn't find all scrums, due to {}".format(e)
        logging.error(errorMsg)
        if not isResponseParsed:
            raise Exception(errorMsg)
        return parseControllerResponse(
            data=None,
            statuscode=500,
            message="Something went wrong, try again later.",
            error=errorMsg,
        )


def findAllScrumsBetweenGivenInterval(start: datetime, end: datetime, **kwargs):
    isResponseParsed = kwargs.get("isParsed", False)

    try:
        scrums: List[ScrumInDBSchema] = findAllScrums(excludeMessages=True)

        # filter the scrums
        print(scrums[0].created_at)
        scrums = [
            scrum
            for scrum in scrums
            if datetime.strptime(scrum.created_at, "%d %b %Y") > start
            and datetime.strptime(scrum.created_at, "%d %b %Y") < end
        ]
        resp = [scrum.dict(exclude={"mongoDocument"}) for scrum in scrums]

        if not isResponseParsed:
            return scrums

        # convert the pydantic obj to a array of dict
        resp = [scrum.dict(exclude={"mongoDocument"}) for scrum in scrums]

        return parseControllerResponse(data=resp, statuscode=200)

    except Exception as e:
        errorMsg = "Couldn't find the scrums between {} and {}, due to {}".format(
            start, end, e
        )
        logging.error(errorMsg)
        if not isResponseParsed:
            raise Exception(errorMsg)
        return parseControllerResponse(
            data=None,
            statuscode=500,
            message="Something went wrong, try again later.",
            error=errorMsg,
        )


def findScrumWithGivenId(scrumId: str, **kwargs):
    try:
        isResponseParsed = kwargs.get("isParsed", False)
        scrum = Scrum.objects(id=scrumId).first()
        if not scrum:
            # scrum with given id doesn't exist
            if isResponseParsed:
                return parseControllerResponse(
                    data=None,
                    statuscode=404,
                    message="A scrum with the given scrum id doesn't exist",
                    error="A scrum with the given scrum id doesn't exist.",
                )
            return None

        if isResponseParsed:
            parsedScrum = ScrumInDBSchema(**scrumHelper(scrum))
            resp = parsedScrum.dict(exclude={"mongoDocument"})
            return parseControllerResponse(
                data=resp, statuscode=200, message="Successfully found the scrum"
            )

        return scrum
    except Exception as e:
        usefulErrorMessage = (
            "Couldn't find the scrum with the given id {}, due to {}".format(scrumId, e)
        )
        logging.error(usefulErrorMessage)

        if isResponseParsed:
            return parseControllerResponse(
                data=None,
                statuscode=500,
                message="Something went wrong try again later",
                error=usefulErrorMessage,
            )

        raise usefulErrorMessage
