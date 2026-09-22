# to define the messages that ShipForge can send to the frontend

from typing import Literal, TypedDict


class BuildStatusEvent(TypedDict):
    type: Literal["status"]
    status: str


class BuildLogEvent(TypedDict):
    type: Literal["log"]
    output: str


BuildEvent = BuildStatusEvent | BuildLogEvent