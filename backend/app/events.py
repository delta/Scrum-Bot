from typing import Callable
import os
import logging

from fastapi import FastAPI

from .database import createConnection, closeConnection
from .logging import setup_logging
from .config import LOGGING_LEVEL

from controllers.constants import initConstants


def createStartAppHandler(app: FastAPI):
    async def startApp():
        setup_logging()
        createConnection()
        initConstants()

    return startApp


def createStopAppHandler(app: FastAPI):
    def closeApp():
        closeConnection()

    return closeApp
