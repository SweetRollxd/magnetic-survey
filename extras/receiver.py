from extras import Point


class Receiver(Point):
    def __init__(self, x: float, y: float, z: float, bx: float = 0, by: float = 0, bz: float = 0):
        super().__init__(x, y, z)
        self.b = (bx, by, bz)
        # self.bx = bx
        # self.by = by
        # self.bz = bz

    def __repr__(self):
        return f"Receiver ({self.x}, {self.z}) with b={self.b}"
