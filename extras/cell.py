from extras import Point
from extras.constants import Axes


class Cell(Point):
    def __init__(self,
                 x: float, y: float, z: float,
                 length, width, height,
                 px: float = 0, py: float = 0, pz: float = 0, ):
        super().__init__(x, y, z)
        self.length = length
        self.width = width
        self.height = height
        self.p = (px, py, pz)

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.z}) with p={self.p}"

    def volume(self):
        return self.length * self.width * self.height
