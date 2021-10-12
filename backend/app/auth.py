import enum
from datetime import datetime
import logging

from fastapi import Header, Depends, Request, HTTPException
from fastapi.exceptions import HTTPException
import jwt
from pydantic import ValidationError

from .config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXPIRE_TIME,
    JWT_TOKEN_PREFIX,
    AUTH_HEADER_KEY,
    BOT_HEADER_KEY,
    BOT_TOKEN_PREFIX,
    BOT_SECRET_TOKEN,
)

from schema.jwt import JWTToken, _JWTUser


class Authorization(object):
    """Class which handles all authentication related logic"""

    class Config:
        schema = {
            "type": "type of authorization",
            "headerName": "Name of the required header",
            "headerPrefix": "Prefix of the required header",
            "headerData": "content header - prefix",
            "payload": "Contents of the decoded header data",  # only for jwt
        }

    allowedAuthorizationTypes = ["jwt", "bot"]

    def __init__(self, **kwargs):
        allowedKeys = ["type"]
        typeInitHandlers = [self._handle_JwtAuthInit, self._handle_BotAuthInit]

        self.__dict__.update(
            ("type", str(v).lower()) for k, v in kwargs.items() if k in allowedKeys
        )

        if self.type not in self.allowedAuthorizationTypes:
            return self._handle_InvalidAuthorizationTypes(self.name)

        for index, value in enumerate(self.allowedAuthorizationTypes):
            if self.type == value:
                typeInitHandlers[index]()

    def authenticateUser(self, request: Request):
        """Find the correct header from the request obj,
        verifies if the header is in the correct format,
        stores the header playload in headerData"""

        # this is the only function which needs to be called while authenticating users
        # this stores all the necessary data and authenticates user

        headerItems = request.headers.items()

        isHeaderFound = False
        for (headerKey, headerValue) in headerItems:
            if headerKey.lower() == self.headerName.lower():
                self._splitHeader(headerValue)
                isHeaderFound = True

        if not isHeaderFound:
            # no auth token, throw a 403\
            return self._handle_Raise403Exception(1, (self.headerName,))

        self.verifyHeaderDataAndStorePayload()
        return self.payload

    def verifyHeaderDataAndStorePayload(self):
        """Verifies the header data, stores payload (if any)"""
        headerVerifiers = [self._decodeJwt, self._verifyBotHeader]
        for index, value in enumerate(self.allowedAuthorizationTypes):
            if self.type == value:
                headerVerifiers[index]()
        return

    # ? helper methods
    def _handle_JwtAuthInit(self):
        self.headerName = AUTH_HEADER_KEY
        self.headerPrefix = JWT_TOKEN_PREFIX

    def _handle_BotAuthInit(self):
        self.headerName = BOT_HEADER_KEY
        self.headerPrefix = BOT_TOKEN_PREFIX

    def _handle_InvalidAuthorizationTypes(self, code):
        raise Exception(
            "Invalid type received for authorization class declaration, got {}".format(
                code
            )
        )

    def _splitHeader(self, header):
        """Splits the header; stores header payload in headerData
        throws 403 error if the  header is invalid"""

        split = header.split()

        if len(split) != 2 or split[0] != self.headerPrefix:
            # header is invalid, raise a 403 error
            return self._handle_Raise403Exception(2, (header,))

        self.headerData = split[1]
        return

    def _decodeJwt(self):
        """Decodes jwt, and stores playload in the obj"""
        try:
            decodedToken = JWTToken(
                **jwt.decode(self.headerData, JWT_SECRET, JWT_ALGORITHM)
            )
            payload = decodedToken

            if payload == None:
                return self._handle_Raise403Exception(3, tuple())

            # Add playload data to the obj
            self.payload = payload
            return True

        except jwt.PyJWTError as decodeError:
            # unable to decode the token,
            # prolly becoz the user is sending random data
            logging.error("Unable to decode jwt, " + str(decodeError))
            return self._handle_Raise403Exception(3, tuple())
        except ValidationError as validationError:

            logging.error("jwt token validation failed" + validationError)
            return self._handle_Raise403Exception(3, tuple())
        except Exception as e:
            print(e)
            logging.error("Decoding jwt failed")
            raise HTTPException(
                status_code=500, detail="Something went wrong. Try again later."
            )

    def _verifyBotHeader(self):
        """Verifies if the bot secret is corret, else throws a 403"""
        if not self.headerData == BOT_SECRET_TOKEN:
            return self._handle_Raise403Exception(4, tuple())
        return True

    def _handle_Raise403Exception(self, errorCode: int, values: tuple):
        """Raises a 403 exception for differnet authentication errors"""

        class ErrorTypes(enum.Enum):
            HeaderNotProvided = 1
            InvalidHeaderFormat = 2
            JWTValidationError = 3
            BotSecretValidationError = 4

        errorDetails = {
            "HeaderNotProvided": "{} header is not provided",
            "InvalidHeaderFormat": "The header entered in in the wrong format {}",
            "JWTValidationError": "Could not validate user. Try again later",
            "BotSecretValidationError": "Bot validation failed",
        }

        def parseErrorMessage():
            try:
                if self.type == "bot":
                    return {
                        "error": errorDetails["BotSecretValidationError"],
                        "message": "Couldn't authenticate user",
                    }
                return {
                    "error": errorDetails[ErrorTypes(errorCode).name].format(*values),
                    "message": "Couldn't authenticate user",
                }
            except Exception as e:
                # this is a mistake on our side, so raise a 500 error
                # with a generic messsage for this
                logging.error("Couldn't generate 403 error message " + e)

                raise Exception(
                    "Invalid data provided for string formatting for 403 error, \
                    for the string {}. But got".format(
                        errorDetails[ErrorTypes(errorCode).name]
                    ),
                    values,
                )

        raise HTTPException(status_code=403, detail=parseErrorMessage())
