import logging

from models.scrum import Scrum
from models.messages import Message

from app.helper import parseControllerResponse

from controllers.constants import findCurrentScrum

from schema.scrum import ScrumInDBSchema, scrumHelper

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
        resp = {
            "scrumId" : newScrum.id.__str__(),
            "scrumName": newScrum.name
        }

        return parseControllerResponse(data=resp, statuscode=200, message="Scrum Created")

    except Exception as e:
        logging.error("Couldn't create a scrum due to ", e)
        raise Exception("Couldn't create a scrum due to ", e)

def findScrumNameWithTheGivenId(id: str):
    """Finds the scrum with the given id and returns its name"""

    try:
        scrum = Scrum.objects(id=id).first()

        resp = {
            "scrumName": scrum.name
        }

        return parseControllerResponse(resp, statuscode=200, message="Scrum Found")

    except Exception as e:
        logging.error("Couldn't find the scrum with the id : {}. Due to".format(id), e)
        raise Exception("Couldn't find the scrum with the id : {}. Due to".format(id), e)

def addMessageToScrum(message: Message):
    """ Adds a a message to the current scrum """
    
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
    try:
        excludeMessages = kwargs.get("excludeMessages", False)
        isResponseParsed = kwargs.get("isParsed", False)

        rawScrums = Scrum.objects() \
            if not excludeMessages \
            else Scrum.objects().fields(messages=0)
        
        
        scrums = [ScrumInDBSchema(**scrumHelper(rawScrum)) for rawScrum in rawScrums]

        if not isResponseParsed:
            return scrums

        # convert the pydantic obj to a array of dict
        resp = [scrum.dict(exclude={"mongoDocument"}) for scrum in scrums]

        return parseControllerResponse(data=resp, statuscode=200)

    except Exception as e:
        errorMsg = "Couldn't find all message, due to {}".format(e)
        logging.error(errorMsg)
        if not isResponseParsed:
            raise Exception(errorMsg)
        return parseControllerResponse(data=None, statuscode=500, 
            message="Something went wrong, try again later.", error="errorMsg")


def findAllDiscussionsOfAScrum(scrumId: str):
    scrum = Scrum.objects(id=scrumId).first()
    if not scrum:
        # scrum with given id doesn't exist
        return None
    return scrum.messages
