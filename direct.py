import math
from matplotlib import pyplot as plt

from extras import Cell, Point, get_mesh, get_receivers, draw_mesh
from generator import generate_mesh


def get_receivers_result(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Point(buf[0],
                               buf[1],
                               buf[2]))
    return receivers


cells_path = 'meshes/cells_1.mes'
receivers_path = 'receivers.dat'

# mesh = get_mesh(cells_path)
start_pnt = Point(-100, -50, -100)
end_pnt = Point(100, 50, -200)
mesh = generate_mesh(start_pnt, end_pnt, 2, 1, 2)
for cell in mesh:
    cell.px = 1
print(mesh)

# print(mesh[0].distance(mesh[1]))

x = []
y = []
receivers_results_path = 'receivers_results.dat'
f = open(receivers_results_path, mode="w")
for rcv_x in range(-1000, 1000, 4):
    # for rcv_x in range(-2000, 3000, 1000):
    receiver = Point(rcv_x, 0, 0)

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
        # print(f"rcv_x = {rcv_x}, Bx = {Bx}")
    f.write(f"{receiver.x} {receiver.y} {receiver.z} {Bx} {By} {Bz}\n")
    x.append(rcv_x)
    y.append(Bx)
f.close()

plt.plot(x, y, marker="o")
plt.grid()
plt.savefig('x_component.png')


recvs = get_receivers(receivers_results_path)
# print(recvs)

draw_mesh('mesh.png', mesh=mesh, receivers=recvs)
