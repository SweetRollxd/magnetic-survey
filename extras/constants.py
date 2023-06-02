from enum import Enum


class Axes(Enum):
    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2


class TaskType(Enum):
    DIRECT = 0
    REVERSE = 1


class MessageTypes(Enum):
    NO_MESH = 0
    NO_RECEIVERS = 1
