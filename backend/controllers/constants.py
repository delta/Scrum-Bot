from fastapi.logger import logging
from models.constants import Constant
from app.config import CONSTANTS, CONSTANTS_DEFAULT_VALUES


def findCurrentScrum():
    try:
        logging.info("Trying to find the current scrum")
        [currentScrum] = Constant.objects(name="currentscrum")
        logging.debug(
            'Got the value "{}", while searching for the current scrum'.format(
                currentScrum.value
            )
        )
        logging.info("Successfully found the current scrum")

        return currentScrum.value
    except Exception as e:
        logging.error("Couldn't find the current scrum due to", e)
        return None


def setCurrentScrum(scrumId=""):
    """Sets the current scrum to the given id, or sets it to a empty string"""
    try:
        logging.info("Trying to set the current active scrum to ", scrumId)
        [currentScrum] = Constant.objects(name="currentscrum")
        currentScrum.value = scrumId
        currentScrum.save()
        logging.info("Successfully set the current active scrum to ", scrumId)
        return True
    except Exception as e:
        logging.error("Couldn't set the current scrum due to ", e)
        return False


def initConstants():
    """Initializes contants, if they do not exist"""

    logging.info("Initialzing Constants in database")

    if len(CONSTANTS) != len(CONSTANTS_DEFAULT_VALUES):
        logging.error("Invalid data given for constants array")

        errorStr = "Invalid CONSTANTS and CONSTANT_DEFAULT_VALUE array provided. \
            CONSTANTS : {}, CONSTANT_DEFAULT_VALUE: {}".format(
            CONSTANTS, CONSTANTS_DEFAULT_VALUES
        )
        logging.error(errorStr)

        raise Exception(errorStr)

    constants = Constant.objects()
    if len(constants) == len(CONSTANTS):
        # All the constants already exist, nth to initialize
        logging.info("Constants have already been initialized.")
        return

    # some constants have not been initialized,
    # find and initialize them
    const_array = CONSTANTS.copy()

    # all constants have been converted to lower case, before saving to database
    # so have to check with lower case
    const_array = [x.lower() for x in const_array]
    const_array_copy = const_array.copy()

    for constant in constants:
        const_array.remove(constant.name)

    logging.debug("The constants {}, need to be initialized".format(const_array))

    for uninitializedConstant in const_array:
        index = const_array_copy.index(uninitializedConstant)
        logging.debug(
            "Creating a new config {} with the value\
                {}".format(
                uninitializedConstant, CONSTANTS_DEFAULT_VALUES[index]
            )
        )
        newConstant = Constant(
            name=uninitializedConstant, value=CONSTANTS_DEFAULT_VALUES[index]
        )
        newConstant.save()

    logging.info("Contants have been initialized, Lessgooo!!")
    return
