import random
from copy import deepcopy

from extras.generator import generate_mesh, generate_receivers
from extras.cell import Cell
from extras.point import Point
from extras.custom_functions import write_mesh_to_file, calculate_receivers, write_receivers_to_file
from extras.receiver import Receiver


class Area:
    def __init__(self, x0, x1, z0, z1):
        self.x0 = x0
        self.x1 = x1
        self.z0 = z0
        self.z1 = z1

    def contains(self, c: Cell):
        return self.x0 * c.length <= c.x < self.x1 * c.length and -self.z0 * c.height > c.z >= -self.z1 * c.height

    def __repr__(self):
        return f"Area '[{self.x0}, {self.x1}], [{self.z0}, {self.z1}]'"


def generate_areas(x_cell_cnt, z_cell_cnt):
    Mx = random.randint(0, x_cell_cnt - 1)
    print(f"Mx = {Mx}")

    division_x = random.sample(range(1, x_cell_cnt), Mx)
    division_x.sort()
    print(f"division_index = {division_x}")

    areas = []
    # divisions = {x_division: [] for x_division in division_index}
    x_start = 0
    z_start = 0
    for i in range(Mx + 1):
        Mz = random.randint(0, z_cell_cnt - 1)
        division_z = random.sample(range(1, z_cell_cnt), Mz)
        division_z.sort()
        print(f"{i}: division_z: {division_z}")
        x_end = division_x[i] if i != Mx else x_cell_cnt

        z_start = 0
        for j in range(Mz + 1):
            z_end = division_z[j] if j != Mz else z_cell_cnt
            # print(f"z_end = {z_end}")
            area = Area(x_start, x_end, z_start, z_end)
            # print(area)
            areas.append(area)
            z_start = z_end
        # if i > 0:
        x_start = x_end

    # print(areas)
    # [print(area) for area in areas]
    return areas


if __name__ == "__main__":
    Nx = 20
    Nz = 10
    start_pnt = Point(0, -50, 0)
    end_pnt = Point(2000, 50, -1000)
    mesh = generate_mesh(start_pnt, end_pnt, count_x=Nx, count_y=1, count_z=Nz)
    # [print(cell) for cell in mesh]
    # random.seed(102)
    areas = generate_areas(Nx, Nz)
    [print(area) for area in areas]
    dataset_size = 1000
    dataset_name = "dataset_0"
    for i in range(dataset_size):
        _mesh = deepcopy(mesh)
        anomalous_area = areas[random.randint(0, len(areas)-1)]
        print(f"Anomalous area = {anomalous_area}")
        for cell in _mesh:
            if anomalous_area.contains(cell):
                cell.p = (1, 0, 0)

        [print(cell) for cell in _mesh]
        dataset_path = f"./datasets/{dataset_name}"
        write_mesh_to_file(f"{dataset_path}/mesh_{i}.mes", _mesh)

        receivers = generate_receivers(start_pnt.x, end_pnt.x, 40)
        calculate_receivers(_mesh, receivers)
        #
        [print(recv) for recv in receivers]
        write_receivers_to_file(f"{dataset_path}/receivers_{i}", receivers)
