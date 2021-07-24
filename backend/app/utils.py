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
)

from schema.jwt import JWTToken, _JWTUser

# generate a jwt with the given data
def generateJwt(data: _JWTUser):
    try:
        algorithm = JWT_ALGORITHM
        jwtSecret = JWT_SECRET
        tokenExpireTime = JWT_EXPIRE_TIME

        payload = JWTToken(**{"sub": data.copy()})

        if tokenExpireTime != 0:
            payload.exp = datetime.now() + tokenExpireTime

        return jwt.encode(payload.dict(), jwtSecret, algorithm=algorithm)
    except Exception as e:
        print("Couldnt generate jwt", e)
        raise Exception(e)


def validateDateString(start: str, end: str):
    """Validates the datesting given for querying scrums"""

    startDateStr = start.split("-")
    endDateStr = end.split("-")

    invalidDateStingErrorMessage = "The given dates {} and {} are of invalid format. \
        It should be of the format DD-MM-YYYY.".format(
        start, end
    )

    try:
        assert len(startDateStr) == 3 and len(endDateStr) == 3, "invalidDateString"

        assert int(endDateStr[2]) > 2000 and int(startDateStr[2]) > 2000, "invalidYear"

        startDate = datetime(
            int(startDateStr[2]), int(startDateStr[1]), int(startDateStr[0])
        )
        endDate = datetime(
            int(endDateStr[2]), int(endDateStr[1]), int(endDateStr[0]) + 1
        )

        assert endDate > startDate, "invalidValues"

        return (startDate, endDate), None

    except AssertionError as e:
        if str(e) == "invalidDateString":
            return (0, 0), invalidDateStingErrorMessage
        if str(e) == "invalidYear":
            return (0, 0), "The year you have entered is invalid"
        if str(e) == "invalidValues":
            return (0, 0), "The start date should be greater than end date"

    except ValueError as _:
        # we get this error when the invalid date is provided for datetime
        # so, return invalid dateStringErrorMessage
        return (0, 0), invalidDateStingErrorMessage
