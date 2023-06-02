import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from extras import Cell, Receiver


def get_receivers(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Receiver(*buf))
    return receivers


def write_receivers(path: str, receivers: list[Receiver]):
    with open(path, mode="w") as f:
        for receiver in receivers:
            f.write(" ".join(map(str, (receiver.x, receiver.y, receiver.z, receiver.bx, receiver.by, receiver.bz))) + "\n")


def get_mesh(path: str) -> list:
    # cells = []
    with open(path, 'r') as f:
        lines = f.readlines()
        print(lines[0])
        length, width, height = lines[0].split(' ')
        cells = [Cell(float(attr[0]),
                      float(attr[1]),
                      float(attr[2]),
                      float(length),
                      float(width),
                      float(height)) for attr in [line.split(' ') for line in lines[1:]]]
        # cells
    # for f in open(path):
    #     buf = [float(attr) for attr in f.split(' ')]
    #     cells.append(Cell(*buf, 100, 100, 50))
        # cells.append(Cell(buf[0],
        #                   buf[1],
        #                   buf[2],
        #                   buf[3]))
    return cells


def draw_mesh(figure: plt.Figure, mesh: list[Cell], receivers: list[Receiver] = None):

    figure.clear()
    ax = figure.add_subplot(111)
    ax.set_title("Сетка")

    ax.axis('equal')
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    ax.grid(True)
    ax.set_axisbelow(True)

    min_px = min(mesh, key=lambda cell: cell.px).px
    max_px = max(mesh, key=lambda cell: cell.px).px

    # TODO: исправить костыль
    if min_px > 0:
        min_px = 0
    if min_px == max_px:
        max_px += min_px + 1
    print(f"Min: {min_px}, max: {max_px}")
    for cell in mesh:
        normalized_px = (cell.px - min_px) / (max_px - min_px)
        text_color = 'w' if normalized_px >= 0.5 else 'k'
        rect = Rectangle((cell.x - cell.length / 2, cell.z - cell.height / 2),
                         cell.length,
                         cell.height,
                         linewidth=1,
                         edgecolor='k',
                         facecolor=f'{1 - normalized_px}')
        ax.add_patch(rect)
        ax.annotate(round(cell.px, 1), (cell.x, cell.z), ha='center', va='center', color=text_color)

    ax.plot()

    if receivers is not None:
        x = []
        z = []
        for r in receivers:
            x.append(r.x)
            z.append(r.z)
            ax.scatter(x, z)

    figure.canvas.draw()


def calculate_receivers(mesh: list, receivers: list):
    for receiver in receivers:
        Bx, By, Bz = 0, 0, 0
        # By = 0
        # B
        for cell in mesh:
            dx = receiver.x - cell.x
            dy = receiver.y - cell.y
            dz = receiver.z - cell.z
            distance = receiver.distance(cell)
            Bx += cell.volume() * 1 / (4 * math.pi * distance ** 3) * (
                    cell.px * (3 * dx * dx / distance ** 2 - 1) +
                    cell.py * (3 * dx * dy / distance ** 2) +
                    cell.pz * (3 * dx * dz / distance ** 2)
            )
            By += cell.volume() * 1 / (4 * math.pi * distance ** 3) * (
                    cell.px * (3 * dx * dy / distance ** 2) +
                    cell.py * (3 * dy * dy / distance ** 2 - 1) +
                    cell.pz * (3 * dy * dz / distance ** 2)
            )
            Bz += cell.volume() * 1 / (4 * math.pi * distance ** 3) * (
                    cell.px * (3 * dx * dz / distance ** 2) +
                    cell.py * (3 * dy * dz / distance ** 2) +
                    cell.pz * (3 * dz * dz / distance ** 2 - 1)
            )
        receiver.bx = Bx
        receiver.by = By
        receiver.bz = Bz


def calculate_mesh(mesh: list, receivers: list, alfa: float):
    L = np.zeros(shape=(len(receivers) * 3, len(mesh) * 3))
    for i, r in enumerate(receivers):
        for j, c in enumerate(mesh):
            dx = r.x - c.x
            dy = r.y - c.y
            dz = r.z - c.z
            dist = r.distance(c)
            mult = c.volume() / (4 * math.pi * dist ** 3)
            L[i * 3][j * 3] += mult * (3 * dx * dx / dist ** 2 - 1)
            L[i * 3][j * 3 + 1] += mult * 3 * dx * dy / dist ** 2
            L[i * 3][j * 3 + 2] += mult * 3 * dx * dz / dist ** 2

            L[i * 3 + 1][j * 3] += mult * 3 * dx * dy / dist ** 2
            L[i * 3 + 1][j * 3 + 1] += mult * (3 * dy * dy / dist ** 2 - 1)
            L[i * 3 + 1][j * 3 + 2] += mult * 3 * dy * dz / dist ** 2

            L[i * 3 + 2][j * 3] += mult * 3 * dx * dz / dist ** 2
            L[i * 3 + 2][j * 3 + 1] += mult * 3 * dy * dz / dist ** 2
            L[i * 3 + 2][j * 3 + 2] += mult * 3 * (dz * dz / dist ** 2 - 1)

    S = [b for r in receivers for b in (r.bx, r.by, r.bz)]

    A = np.matmul(L.transpose(), L)
    b = np.matmul(L.transpose(), S)
    # print(f"A = {A}")
    # print(f"b = {b}")

    ones = np.eye(len(A))
    regularizedA = A + np.dot(alfa, ones)
    p = np.linalg.solve(regularizedA, b)

    for i, c in enumerate(mesh):
        c.px = p[i * 3]
        c.py = p[i * 3 + 1]
        c.pz = p[i * 3 + 2]

    return mesh
