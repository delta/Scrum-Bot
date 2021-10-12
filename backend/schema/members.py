from typing import Optional, List
from pydantic import BaseModel, Field, validator, PrivateAttr
import hashlib
import os

from schema.dbmodel import DBModelMixin


class CreateMemberSchema(BaseModel):
    """Member Schema"""

    name: str = Field(...)
    rollno: int = Field(
        ..., gt=100000000, lt=200000000
    )  # random, make sure the rollno is 9 digit
    password: str = Field(...)
    batch: int = Field(...)
    discordHandle: str = Field(...)
    password_repeat: str = Field(...)

    # Check if the discordHandle contains a '#'
    @validator("discordHandle")
    def discordHandleMustContainHash(cls, v):
        if "#" not in v:
            raise ValueError("Discord handle must contain '#'")
        return v

    # Check if password is at least 6 characters long
    @validator("password")
    def passwordLongEnough(cls, v):
        if len(v) < 6:
            raise ValueError("Password is too short")
        return v

    # check if password and repeat_password match
    @validator("password_repeat")
    def checkPasswordMatch(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v

    # helper function to generate salt and hash for the password
    def hasPassword(self):
        self.password = self.hashGivenText(self.password)
        return

    @staticmethod
    def hashGivenText(self, password: str):
        # genrates 32 random bytes
        salt = os.urandom(32)
        salt = salt.hex()
        # key is generated using https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac
        # reccomended to use at least 10^6 iterations of sha_256
        # generates 128 bit key
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(1e6),
            dklen=128,
        )
        password = salt + "." + key.hex()
        return password

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "rollno": 112119006,
                "batch": 2023,
                "discordHandle": "john#1234",
                "password": "password123",
                "password_repeat": "password123",
            }
        }


class UpdateMemberSchema(BaseModel):
    """Update member Member Schema.
    Must contain roll no. Can contain one or more field from {name, batch, discordHandle, password, password_repeat}"""

    name: Optional[str]
    rollno: int = Field(...)
    batch: Optional[int]
    discordHandle: Optional[str]
    password: Optional[str]
    password_repeat: Optional[str]

    # Check if the discordHandle contains a '#' if it exists
    @validator("discordHandle")
    def discordHandleMustContainHash(cls, v, values):
        if not v:
            return None
        if "#" not in v:
            raise ValueError("Discord handle must contain '#'")
        return v

    # Check if password is at least 6 characters long
    @validator("password")
    def passwordLongEnough(cls, v, values, **kwargs):
        if not v:
            return None
        if len(v) < 6:
            raise ValueError("Password is too short")
        return v

    # check if password and repeat_password match
    @validator("password_repeat", always=True)
    def checkPasswordMatch(cls, v, values):
        if "password" not in values and not v:
            return None
        if v != values["password"]:
            raise ValueError("passwords do not match")
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "rollno": 112119006,
                "batch": 2023,
                "discordHandle": "john#1234",
                "password": "password123",
                "password_repeat": "password123",
            }
        }


class LoginModel(BaseModel):
    """Login Model Schema"""

    rollno: int = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {"example": {"rollno": 112119006, "password": "password123"}}


class MemberInDBSchema(DBModelMixin):
    """Schema for a single  member in database"""

    name: str = Field(...)
    rollno: int = Field(...)
    _password: str = PrivateAttr(
        ...
    )  # it is a private attribute and wont be present when we call dict method
    batch: int = Field(...)
    discordHandle: str = Field(...)

    def __init__(self, **data):
        super().__init__(**data)
        self._password = data["_password"]

    def verifyPassword(self, inputPassword: str):
        """check if the password and the inputPassword matches

        Args:
            inputPassword (str): plain text password entered by the user which logging in the

        Returns:
            Bool: True if the password matches, False otherwise False"""

        try:
            [salt, key] = self._password.split(".")
            # salt = bytes(salt, "utf-8")
            inputKey = hashlib.pbkdf2_hmac(
                "sha256",
                inputPassword.encode("utf-8"),
                salt.encode("utf-8"),
                int(1e6),
                dklen=128,
            )

            if inputKey.hex() == key:
                return True
            return False
        except Exception as e:
            # there shdnt be any exception
            print("err : ", e)


class SingleMemberResponseModel(BaseModel):
    id: str = Field(...)
    objId: str = Field(...)
    name: str = Field(...)
    rollno: int = Field(...)
    batch: int = Field(...)
    discordHandle: str = Field(...)


class GetAllMembersResponseModel(BaseModel):
    members: List[SingleMemberResponseModel]


class GetSingleMemberResponseModel(BaseModel):
    member: SingleMemberResponseModel


class GetMyUserModel(GetSingleMemberResponseModel):
    pass


class UpdateMyUserModel(GetSingleMemberResponseModel):
    pass


# HELPER FUNCTIONS


def memberHelper(member):
    """converts a single member document returned by mongo to a dict"""
    return {
        "id": member["id"],
        "objId": str(member["id"]),
        "name": member["name"],
        "rollno": member["rollno"],
        "_password": member["password"],
        "batch": member["batch"],
        "discordHandle": member["discordHandle"],
        "mongoDocument": member,
    }
