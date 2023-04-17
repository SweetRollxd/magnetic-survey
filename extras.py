import math
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle


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


# TODO: сделать в ячейке список узлов
class Cell(Point):
    length = 200
    width = 200
    height = 200
    I = 1

    def __init__(self, x: float, y: float, z: float, px: float):
        super().__init__(x, y, z)
        self.px = px

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.z}) with px={self.px}"

    def volume(self):
        return self.length * self.width * self.height

def get_receivers(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Point(buf[0],
                               buf[1],
                               buf[2]))
    return receivers


def get_mesh(path: str) -> list:
    cells = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        cells.append(Cell(buf[0],
                          buf[1],
                          buf[2],
                          buf[3]))
    return cells


# TODO: рисование сетки по координатам узлов ячейки
def draw_mesh(path: str, mesh: list, receivers):

    fig, ax = plt.subplots(figsize=(16.0, 4.8))
    x = []
    z = []
    for r in receivers:
        x.append(r.x)
        z.append(r.z)

    ax.scatter(x, z)
    ax.axis('equal')
    for cell in mesh:
        print(cell.x, cell.z, cell.width)
        rect = Rectangle((cell.x - cell.width / 2, cell.z - cell.height / 2),
                         cell.width,
                         cell.height,
                         linewidth=2,
                         edgecolor='none',
                         facecolor=f'{1 - cell.px}')
        ax.add_patch(rect)
        ax.annotate(cell.px, (cell.x, cell.z), color=f'{cell.px}')

    plt.savefig(path)