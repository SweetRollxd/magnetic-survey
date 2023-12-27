import copy
import math
import random
import json

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import *


def print_arrays(indexes_x, indexes_y):
    mx = len(indexes_x)
    print("ind_x: (", mx, ")")
    for i in range(mx):
        print(indexes_x[i], " ", end='')
    print()

    for i in range(mx + 1):
        print("ind_y", i, ": ", end='')
        for j in indexes_y[i]:
            print(j, " ", end='')
        print()


def make_small_areas_arrays(area):
    na = 0  # omega - areas' count
    indexes_y = []
    mx = random.randint(0, area.nx - 1)
    indexes_x = random.sample(range(1, area.nx), mx)
    indexes_x.sort()

    for i in range(mx + 1):
        mz = random.randint(0, area.nz - 1)
        na += mz
        tmp = random.sample(range(1, area.nz), mz)
        tmp.sort()
        indexes_y.append(tmp)
    return indexes_x, indexes_y


def init(area):
    cells = []
    hx = (area.xmax - area.xmin) / area.nx
    hz = (area.zmax - area.zmin) / area.nz
    curx = area.xmin
    curz = area.zmin

    for j in range(area.nz):
        tmp_cells = []
        for i in range(area.nx):
            cell = Cell(curx + i * hx, curx + (i + 1) * hx, area.ymin, area.ymax, curz + j * hz, curz + (j + 1) * hz, 0)
            tmp_cells.append(cell)
        cells.append(tmp_cells)
    area.cells = cells


def init_rec(xmin, xmax, nrec):
    rec = []
    hrec = (xmax - xmin) / (nrec - 1)
    for i in range(nrec):
        rec.append(xmin + hrec * i)
    return rec


def B_for_rec_for_cell(cur_cell, cur_rec):
    hx = cur_cell.xmax - cur_cell.xmin
    hy = cur_cell.ymax - cur_cell.ymin
    hz = cur_cell.zmax - cur_cell.zmin
    mes = hx * hy * hz
    barycenter = {'x': (cur_cell.xmax + cur_cell.xmin) / 2, 'y': (cur_cell.ymax + cur_cell.ymin) / 2,
                  'z': (cur_cell.zmax + cur_cell.zmin) / 2};
    xv = cur_rec - barycenter['x']
    yv = - barycenter['y']
    zv = - barycenter['z']
    r = math.sqrt(xv * xv + yv * yv + zv * zv)
    B = mes / (4 * math.pi * r * r * r) * (cur_cell.px * (3 * xv * zv / (r * r)));
    return B


def B_for_rec(area, cur_rec):
    B_cur = 0
    for i in range(len(area.cells)):
        for j in range(len(area.cells[i])):
            B_cur += B_for_rec_for_cell(area.cells[i][j], cur_rec)
    return B_cur


def direct_task(area, receivers):
    B = []
    for i in range(len(receivers)):
        B.append(B_for_rec(area, receivers[i]))
    return B


def add_anom_to_area(area, xmin, xmax, zmin, zmax, px_anom, iter, k):
    cur_area = copy.deepcopy(area)
    p = []
    # add anoms
    for i in range(xmin, xmax):
        for j in range(zmin, zmax):
            cur_area.cells[j][i].px = px_anom

    paint_area(cur_area, iter, k)
    return cur_area


def make_area_p_B_array(area, receivers, ):
    p = []
    for i in range(len(area.cells)):
        for j in range(len(area.cells[i])):
            p.append(area.cells[i][j].px)
    B = direct_task(area, receivers)
    return p, B


def make_dataset(area, receivers, px_anom):
    k = 0  # текущий номер области
    datasetP = []
    datasetB = []

    for iter in range(100):
        print(iter)
        k = 0
        ind_x, ind_y = make_small_areas_arrays(area)
        xmin = 0
        for i in range(len(ind_x)):
            xmax = ind_x[i]
            zmin = 0
            for j in range(len(ind_y[i])):
                zmax = ind_y[i][j]
                cur_area = add_anom_to_area(area, xmin, xmax, zmin, zmax, px_anom, iter, k)
                cur_p, cur_B = make_area_p_B_array(cur_area, receivers)
                datasetP.append(cur_p)
                datasetB.append(cur_B)
                k += 1
                zmin = zmax
            # last z area
            zmax = area.nz
            cur_area = add_anom_to_area(area, xmin, xmax, zmin, zmax, px_anom, iter, k)
            cur_p, cur_B = make_area_p_B_array(cur_area, receivers)
            datasetP.append(cur_p)
            datasetB.append(cur_B)
            k += 1

            xmin = xmax

        # last x area
        xmax = area.nx
        zmin = 0
        i = len(ind_x)
        for j in range(len(ind_y[i])):
            zmax = ind_y[i][j]
            cur_area = add_anom_to_area(area, xmin, xmax, zmin, zmax, px_anom, iter, k)
            cur_p, cur_B = make_area_p_B_array(cur_area, receivers)
            datasetP.append(cur_p)
            datasetB.append(cur_B)
            k += 1
            zmin = zmax
        # last z area
        zmax = area.nz
        cur_area = add_anom_to_area(area, xmin, xmax, zmin, zmax, px_anom, iter, k)
        cur_p, cur_B = make_area_p_B_array(cur_area, receivers)
        datasetP.append(cur_p)
        datasetB.append(cur_B)
        k += 1
    return datasetP, datasetB


def print_dataset(dataset):
    for i in dataset:
        print(i)


def print_in_file(dataset, filename):
    f = open(filename, 'w')
    f.write(json.dumps(dataset))
    f.close()


def paint_area(area, iter, k):
    hx = (area.xmax - area.xmin) / area.nx
    hz = (area.zmax - area.zmin) / area.nz

    fig, ax = plt.subplots()
    ax.set_title('Lines')
    plt.axis([area.xmin, area.xmax, area.zmin, area.zmax])

    ax.xaxis.set_major_locator(ticker.MultipleLocator(hx))  # интервал основных делений
    ax.yaxis.set_major_locator(ticker.MultipleLocator(hz))
    plt.xlabel('x', fontsize=12)
    plt.ylabel('z', fontsize=12)
    plt.grid()

    for i in range(len(area.cells)):
        for j in range(len(area.cells[i])):
            a = area.cells[i][j]
            if (a.px):
                rect = Rectangle((a.xmin, a.zmin), (a.xmax - a.xmin), (a.zmax - a.zmin), facecolor='g')
                ax.add_patch(rect)
    filename = 'dataset/fig' + str(iter) + '_' + str(k) + '.png'
    plt.savefig(filename)
    plt.close(fig)


class Area:
    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax, nx, nz):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.nx = nx
        self.nz = nz
        self.cells = []


class Cell:
    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax, px):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.px = px


def main_func():
    ymin = -500
    ymax = 500
    area = Area(0, 1000, -500, 500, -500, 0, 10, 5)
    init(area)

    receivers = init_rec(area.xmin, area.xmax, 100)
    datasetP, datasetB = make_dataset(area, receivers, 1)
    print_in_file(datasetP, 'datasetP.txt')
    print_in_file(datasetB, 'datasetB.txt')
    return datasetP, datasetB


if __name__ == '__main__':
    main_func()
