import math
import numpy
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
    # length = 200
    # width = 200
    # height = 100
    # I = 1

    def __init__(self,
                 x: float, y: float, z: float,
                 length, width, height,
                 px: float = 0, py: float = 0, pz: float = 0,):
        super().__init__(x, y, z)
        self.length = length
        self.width = width
        self.height = height
        self.px = px
        self.py = py
        self.pz = pz

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.z}) with px={self.px}, py={self.py}, pz={self.pz}"

    def volume(self):
        return self.length * self.width * self.height


class Receiver(Point):
    def __init__(self, x: float, y: float, z: float, bx: float, by: float, bz: float):
        super().__init__(x, y, z)
        self.bx = bx
        self.by = by
        self.bz = bz


def get_receivers(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Receiver(*buf))
    return receivers


def get_mesh(path: str) -> list:
    cells = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        cells.append(Cell(*buf, 200, 200, 100))
        # cells.append(Cell(buf[0],
        #                   buf[1],
        #                   buf[2],
        #                   buf[3]))
    return cells


# TODO: рисование сетки по координатам узлов ячейки
def draw_mesh(path: str, mesh: list, receivers: list = None):

    if receivers is None:
        receivers = []
    fig, ax = plt.subplots(figsize=(16.0, 4.8))
    x = []
    z = []
    for r in receivers:
        x.append(r.x)
        z.append(r.z)

    ax.scatter(x, z)
    ax.axis('equal')
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    # ax.grid(True)
    # ax.set_xticks(numpy.arange(-2000, 2000, 200))
    # ax.set_yticks(numpy.arange(-1000, 200, 100))

    # ax.set_ylim([-400, 100])

    min_px = min(mesh, key=lambda cell: cell.px).px
    max_px = max(mesh, key=lambda cell: cell.px).px

    # TODO: исправить костыль
    if min_px > 0:
        min_px = 0

    print(f"Min: {min_px}, max: {max_px}")
    for cell in mesh:
        # print(cell.x, cell.z, cell.width)
        print(f"px = {cell.px}")
        rect = Rectangle((cell.x - cell.length / 2, cell.z - cell.height / 2),
                         cell.length,
                         cell.height,
                         linewidth=1,
                         # edgecolor='none',
                         edgecolor='k',
                         facecolor=f'{1 - (cell.px - min_px)/(max_px - min_px)}')
        ax.add_patch(rect)
        ax.annotate(round(cell.px, 1), (cell.x, cell.z), ha='center', va='center', color=f'{(cell.px - min_px)/(max_px - min_px)}')
    # plt.grid()
    plt.ylim([-400, 100])
    plt.savefig(path)
