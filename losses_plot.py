import matplotlib.pyplot as plt
from numpy.distutils.system_info import xft_info

# losses = []

with open("losses.txt", "r") as f:
    losses = [float(l) for l in f.readlines()]

print(losses)

# fig, ax = plt.figure(figsize=(8.0, 2.4), constrained_layout=True)

plt.plot(losses)
plt.xlabel("Номер эпохи")
plt.ylabel("Значение функции потерь")
plt.grid()
# plt.savefig("losses.png")
plt.show()