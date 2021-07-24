from mongoengine import connect, disconnect
from pymongo import monitoring
import logging

from .config import MONGO_URI

log = logging.getLogger()
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class CommandLogger(monitoring.CommandListener):
    def started(self, event):
        log.debug(
            "Command {0.command_name} with request id "
            "{0.request_id} started on server "
            "{0.connection_id}".format(event)
        )

    def succeeded(self, event):
        log.debug(
            "Command {0.command_name} with request id "
            "{0.request_id} on server {0.connection_id} "
            "succeeded in {0.duration_micros} "
            "microseconds".format(event)
        )

    def failed(self, event):
        log.debug(
            "Command {0.command_name} with request id "
            "{0.request_id} on server {0.connection_id} "
            "failed in {0.duration_micros} "
            "microseconds".format(event)
        )


def createConnection():
    monitoring.register(CommandLogger())
    connect(host=MONGO_URI)
    logging.info("Connected to the database %s", MONGO_URI)


def closeConnection():
    disconnect()
    logging.info("Disconnected from the database %s", MONGO_URI)
