import math
import numpy as np
import copy
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import TransformedBbox, Bbox
import os

from extras import Cell, Receiver
from extras.constants import Axes


def read_receivers_from_file(fname: str | os.PathLike) -> list:
    receivers = []
    for f in open(fname):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Receiver(*buf))
    return receivers


def write_receivers_to_file(fname: str, receivers: list[Receiver]):
    if fname[-4:] != '.dat':
        fname += '.dat'
    with open(fname, mode="w") as f:
        for receiver in receivers:
            f.write(" ".join(map(str, (receiver.x, receiver.y, receiver.z, *receiver.b))) + "\n")


def read_mesh_from_file(fname: str | os.PathLike) -> list:
    with open(fname, 'r') as f:
        lines = f.readlines()
        print(lines[0])
        length, width, height = lines[0].split(' ')
        cells = [Cell(*list(map(float, attr[0:3])), *list(map(float, (length, width, height))), *list(map(float, attr[3:]))) for attr in [line.split(' ') for line in lines[1:]]]
        # cells
    # for f in open(fname):
    #     buf = [float(attr) for attr in f.split(' ')]
    #     cells.append(Cell(*buf, 100, 100, 50))
        # cells.append(Cell(buf[0],
        #                   buf[1],
        #                   buf[2],
        #                   buf[3]))
    return cells


def write_mesh_to_file(fname, mesh):
    if fname[-4:] != '.mes':
        fname += '.mes'
    with open(fname, mode='w') as f:
        f.write(" ".join(map(str, (mesh[0].length, mesh[0].width, mesh[0].height))) + '\n')
        for cell in mesh:
            f.write(" ".join(map(str, (cell.x, cell.y, cell.z, cell.p[0], cell.p[1], cell.p[2]))) + '\n')


def draw_mesh(figure: plt.Figure, mesh: list[Cell],
              receivers: list[Receiver] = None,
              axis: Axes = Axes.X,
              title: str = "",
              x_lim: tuple[float, float] = None,
              y_lim: tuple[float, float] = None):
    figure.clear()
    ax = figure.add_subplot(111)
    ax.set_title(f"{title} ({Axes(axis).name}-компонента)")

    # ax.axis('equal')
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    ax.grid(True)
    ax.set_axisbelow(True)

    ax.set_ylabel('Z, м')
    ax.set_xlabel('X, м')
    values = [cell.p[axis.value] for cell in mesh]
    # min_value = min(values)
    # max_value = max(values)
    min_value = 0
    max_value = 1

    # if min_value > 0:
    #     min_value = 0
    # if max_value > 1:
    #     max_value = 1
    # if min_value == max_value:
    #     max_value += max_value + 1
    # print(f"Min: {min_value}, max: {max_value}")

    for cell in mesh:
        value = cell.p[axis.value]
        # normalized_value = (value - min_value) / (max_value - min_value)
        if value > 1:
            normalized_value = 1
        elif value < 0:
            normalized_value = 0
        else:
            normalized_value = (value - min_value) / (max_value - min_value)
        text_color = 'w' if normalized_value >= 0.5 else 'k'
        rect = Rectangle((cell.x - cell.length / 2, cell.z - cell.height / 2),
                         cell.length,
                         cell.height,
                         linewidth=1,
                         edgecolor='k',
                         facecolor=f'{1 - normalized_value}')
        ax.add_patch(rect)
        box = TransformedBbox(Bbox([[cell.x - cell.length / 2, cell.z - cell.height / 2], [cell.x + cell.length / 2, cell.z + cell.height / 2]]), ax.transData)
        ax.annotate(round(cell.p[axis.value], 1), (cell.x, cell.z), ha='center', va='center', color=text_color, clip_box=box)

    ax.plot()
    ax.set_xlim(x_lim) if x_lim else None
    ax.set_ylim(y_lim) if y_lim else None

    if receivers is not None:
        x = []
        z = []
        for r in receivers:
            x.append(r.x)
            z.append(r.z)
            ax.scatter(x, z, marker='|')

    figure.canvas.draw()


def draw_plot(figure: plt.Figure,
              receivers: list[Receiver],
              axis: Axes = Axes.X,
              x_lim: tuple[float, float] = None,
              y_lim: tuple[float, float] = None):
    figure.clear()
    ax = figure.add_subplot(111)
    ax.set_xlabel('X, м')
    ax.set_ylabel(f'B{Axes(axis).name.lower()}, Тл')
    ax.set_title(f"{Axes(axis).name}-компонента магнитного поля B")
    x = [receiver.x for receiver in receivers]
    values = [receiver.b[axis.value] for receiver in receivers]
    ax.plot(x, values)
    ax.grid()

    ax.set_xlim(x_lim) if x_lim else None
    ax.set_ylim(y_lim) if y_lim else None
    figure.canvas.draw()


def calculate_receivers(mesh: list[Cell], receivers: list[Receiver]) -> list[Receiver]:
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
                    cell.p[0] * (3 * dx * dx / distance ** 2 - 1) +
                    cell.p[1] * (3 * dx * dy / distance ** 2) +
                    cell.p[2] * (3 * dx * dz / distance ** 2)
            )
            By += cell.volume() * 1 / (4 * math.pi * distance ** 3) * (
                    cell.p[0] * (3 * dx * dy / distance ** 2) +
                    cell.p[1] * (3 * dy * dy / distance ** 2 - 1) +
                    cell.p[2] * (3 * dy * dz / distance ** 2)
            )
            Bz += cell.volume() * 1 / (4 * math.pi * distance ** 3) * (
                    cell.p[0] * (3 * dx * dz / distance ** 2) +
                    cell.p[1] * (3 * dy * dz / distance ** 2) +
                    cell.p[2] * (3 * dz * dz / distance ** 2 - 1)
            )
        receiver.b = (Bx, By, Bz)
    return receivers


def calculate_mesh(mesh: list[Cell], receivers: list[Receiver], alfa: float) -> list[Cell]:
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

    S = [b for r in receivers for b in r.b]

    A = np.matmul(L.transpose(), L)
    b = np.matmul(L.transpose(), S)

    # print(f"Alfa={alfa}, A={A}, b={b}")

    ones = np.eye(len(A))
    regularizedA = A + np.dot(alfa, ones)
    p = np.linalg.solve(regularizedA, b)

    for i, c in enumerate(mesh):
        c.p = p[i*3:i*3+3]

    return mesh


def calculate_receivers_error(true_receivers: list[Receiver], calculated_receivers: list[Receiver]) -> float:
    error = 0
    for i in range(len(true_receivers)):
        for j in range(3):
            error += math.pow(true_receivers[i].b[j] - calculated_receivers[i].b[j], 2)
    return error
