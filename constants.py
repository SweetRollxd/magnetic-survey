from enum import Enum


class Axes(Enum):
    X_AXIS = 1
    Y_AXIS = 2
    Z_AXIS = 3


class TaskType(Enum):
    DIRECT = 1
    REVERSE = 2