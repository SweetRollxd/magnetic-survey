import math
from matplotlib import pyplot as plt

from extras import Cell, Point, get_mesh, get_receivers, draw_mesh

def get_receivers_result(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Point(buf[0],
                               buf[1],
                               buf[2]))
    return receivers

cells_path = 'cells.dat'
receivers_path = 'receivers.dat'

mesh = get_mesh(cells_path)
print(mesh)

print(mesh[0].distance(mesh[1]))

# TODO: добавить компоненты py и pz
# x = []
# y = []
receivers_results_path = 'receivers_results.dat'
# f = open(receivers_results_path, mode="w")
# for rcv_x in range(-2000, 2000, 50):
#     receiver = Point(rcv_x, 0, 0)
#     Bx = 0
#     for cell in mesh:
#         Bx += cell.volume() * cell.I / (4 * math.pi * receiver.distance(cell) ** 3) * \
#               (cell.px * (3 * (receiver.x - cell.x) ** 2) / receiver.distance(cell) ** 2 - 1)
#     f.write(f"{receiver.x} {receiver.y} {receiver.z} {Bx}\n")
#     x.append(rcv_x)
#     y.append(Bx)
# f.close()
#
# plt.plot(x, y, marker="o")
# plt.savefig('x_component.png')

recvs = get_receivers(receivers_results_path)
print(recvs)

draw_mesh('mesh.png', mesh=mesh, receivers=recvs)