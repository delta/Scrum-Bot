import logging
from mongoengine.errors import ValidationError, NotUniqueError
from models.members import Member
from schema.members import memberHelper, MemberInDBSchema
from app.helper import parseControllerResponse
from app.utils import generateJwt


# Add users to database
def register(user):
    try:
        logging.info("Creating a new user with the data " + str(user))
        newUser = Member(rollno=user["rollno"])
        newUser.name = user["name"]
        newUser.password = user["password"]
        newUser.batch = user["batch"]
        newUser.discordHandle = user["discordHandle"]
        newUser.password = user["password"]

        newUser.save(force_insert=False, validate=True)

        return parseControllerResponse(
            data="Success", statuscode=200, message="Successfully created a user"
        )
    except ValidationError as err:
        logging.debug(
            "Something went wrong, couldn't validate data for the user {} \
            and got the error {}".format(
                user, err
            )
        )
        return parseControllerResponse(
            data="", statuscode=400, error=err, message="Data entered is incorrect"
        )

    except NotUniqueError as err:
        # There is no way to create user friendly message
        # So converting it into a string and checking if the rollno is there in the sub string
        if "rollno" in err.__str__():
            return parseControllerResponse(
                data="Failure",
                statusCode=11000,
                error='A user already exists with the rollno "{}"'.format(
                    user["rollno"]
                ),
                message="A document with the given data already exists",
            )
        return parseControllerResponse(
            data="Failure",
            statuscode=11000,
            error='A user already exists with the Discord Handle "{}"'.format(
                user["discordHandle"]
            ),
            message="A document with the given data already exists",
        )

    except Exception as e:
        logging.error("Couldn't create document for {}. Due to {}".format(user, e))
        return parseControllerResponse(
            data="Failure",
            statuscode=500,
            error=e,
            message="Something went wrong, try again later.",
        )


def login(rollnumber, password):
    try:
        error_message = "The rollno password combination is incorrect"
        userDoc = Member.objects(rollno=rollnumber)
        # user not found
        if len(userDoc) == 0:
            return parseControllerResponse(
                data="Failure",
                statuscode=400,
                error=error_message,
                message=error_message,
            )
        user = MemberInDBSchema(**memberHelper(userDoc[0]))
        doesPasswordMatch = user.verifyPassword(password)
        if doesPasswordMatch:
            # Create session and return a 200

            token = generateJwt({"id": str(user.objId), "rollno": user.rollno})
            return parseControllerResponse(
                data={"token": token},
                statuscode=200,
                message="User successfully authenticated",
            )

        else:
            return parseControllerResponse(
                data="Failure",
                statuscode=400,
                error=error_message,
                message=error_message,
            )

    except Exception as err:
        logging.error("Couldn't authenticate {}. Due to {}".format(rollnumber, err))
        return parseControllerResponse(
            data="Failure",
            statuscode=500,
            error=err,
            message="Something went wrong, try again later.",
        )
