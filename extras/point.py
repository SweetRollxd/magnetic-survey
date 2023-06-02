import math


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def distance(self, other_point):
        return math.sqrt((self.x - other_point.x) ** 2 +
                         (self.y - other_point.y) ** 2 +
                         (self.z - other_point.z) ** 2)