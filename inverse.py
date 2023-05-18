import numpy as np

from extras import Cell, Point, get_mesh, get_receivers

class Receiver(Point):
    def __init__(self, x: float, y: float, z: float, bx: float):
        super().__init__(x, y, z)
        self.bx = bx


def get_receivers(path: str) -> list:
    receivers = []
    for f in open(path):
        buf = [float(attr) for attr in f.split(' ')]
        receivers.append(Receiver(buf[0],
                                  buf[1],
                                  buf[2],
                                  buf[3]))
    return receivers

receivers_results_path = 'receivers_results.dat'
mesh_path = 'mesh.dat'

mesh = get_mesh(mesh_path)
receivers = get_receivers(receivers_results_path)
# L = np.zeros(shape=(len(receivers) * 3, len(mesh) * 3))
L = np.zeros(shape=(len(receivers), len(mesh) * 3))
# S = np.zeros(len(receivers) * 3)
for i, r in enumerate(receivers):
    for j, c in enumerate(mesh):
        L[i][j*3] += 3 * (r.x - c.x) ** 2 / (r.distance(c) ** 2) - 1
        L[i][j*3+1] += 3 * (r.x - c.x) * (r.y - c.y) / (r.distance(c) ** 2)
        L[i][j*3+2] += 3 * (r.x - c.x) * (r.z - c.z) / (r.distance(c) ** 2)
    # S[i*3] = r.bx
S = [r.bx for r in receivers]
print(f"L = {L}")
print(f"S = {S}")

# C = np.zeros(shape=(len(receivers), len(mesh) * 3))


A = np.matmul(L.transpose(), L)
b = np.matmul(L.transpose(), S)
print(f"A = {A}")
print(f"b = {b}")

alfa = 10**-1
alfa = 1
ones = np.eye(len(A))
# print(np.dot(alfa, ones))
regularizedA = A + np.dot(alfa, ones)
print(np.linalg.det(regularizedA))
p = np.linalg.solve(regularizedA, b)
print(f"p={p}")