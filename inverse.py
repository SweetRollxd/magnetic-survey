import math

import numpy as np

from extras import get_mesh, get_receivers, draw_mesh

receivers_results_path = 'receivers_results.dat'
mesh_path = 'mesh_16.dat'

mesh = get_mesh(mesh_path)
receivers = get_receivers(receivers_results_path)
L = np.zeros(shape=(len(receivers) * 3, len(mesh) * 3))
# L = np.zeros(shape=(len(receivers), len(mesh) * 3))
for i, r in enumerate(receivers):
    for j, c in enumerate(mesh):
        dx = r.x - c.x
        dy = r.y - c.y
        dz = r.z - c.z
        dist = r.distance(c)
        mult = c.volume() / (4 * math.pi * dist ** 3)
        L[i*3][j*3] += mult * (3 * dx * dx / dist ** 2 - 1)
        L[i*3][j*3+1] += mult * 3 * dx * dy / dist ** 2
        L[i*3][j*3+2] += mult * 3 * dx * dz / dist ** 2

        L[i*3+1][j*3] += mult * 3 * dx * dy / dist ** 2
        L[i*3+1][j*3+1] += mult * (3 * dy * dy / dist ** 2 - 1)
        L[i*3+1][j*3+2] += mult * 3 * dy * dz / dist ** 2

        L[i*3+2][j*3] += mult * 3 * dx * dz / dist ** 2
        L[i*3+2][j*3+1] += mult * 3 * dy * dz / dist ** 2
        L[i*3+2][j*3+2] += mult * 3 * (dz * dz / dist ** 2 - 1)

S = [b for r in receivers for b in (r.bx, r.by, r.bz)]
# print(f"L = {L}")
# print(f"S = {S}")

# C = np.zeros(shape=(len(receivers), len(mesh) * 3))


A = np.matmul(L.transpose(), L)
b = np.matmul(L.transpose(), S)
# print(f"A = {A}")
# print(f"b = {b}")

# alfa = 10**-2
alfa = 0
ones = np.eye(len(A))
regularizedA = A + np.dot(alfa, ones)
p = np.linalg.solve(regularizedA, b)
print(f"p={p}")

for i, c in enumerate(mesh):
    c.px = p[i*3]
    c.py = p[i*3+1]
    c.pz = p[i*3+2]
    # print(c, f"px={p[i*3]}, py={p[i*3+1]}, pz={p[i*3+2]}")
    print(c)

draw_mesh('result_mesh.png', mesh, receivers)