from enum import Enum


class Axes(Enum):
    X = 0
    Y = 1
    Z = 2


class TaskType(Enum):
    DIRECT = 0
    REVERSE = 1


class MessageTypes(Enum):
    NO_MESH = 0
    NO_RECEIVERS = 1
    WRONG_INPUT = 2
