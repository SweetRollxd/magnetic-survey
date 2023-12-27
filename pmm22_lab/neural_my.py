import json
import math
import numpy as np
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as path
import dataset

from extras.custom_functions import read_mesh_from_file, read_receivers_from_file, write_mesh_to_file
from extras.generator import generate_mesh
from extras.point import Point

def read_dataset():
    dataset = []
    f = open('datasetP.txt', 'r')
    f1 = open('datasetB.txt', 'r')
    a = f.read()
    a1 = f1.read()
    datasetP = json.loads(a)
    datasetB = json.loads(a1)
    f.close()
    for i in range(len(datasetP)):
        px = torch.tensor(datasetP[i], dtype=torch.float32)
        Bz = torch.tensor(datasetB[i], dtype=torch.float32)
        dataset.append([Bz, px])
    return dataset


def create_nn(dataset_train, dataset_test, epochs=100):
    initSize = len(dataset_train[0][0])
    hideSize = 2 * initSize
    outSize = len(dataset_train[0][1])

    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.fc1 = nn.Linear(initSize, hideSize)
            self.fc2 = nn.Linear(hideSize, outSize)

        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return F.relu(x)

    net = Net()
    optimizer = optim.SGD(net.parameters(), lr=0.01, momentum=0.9)
    criterion = nn.MSELoss()

    sumL = 0
    for i in range(len(dataset_train)):
        net_out = net(dataset_train[i][0])
        target = dataset_train[i][1]
        loss = criterion(net_out, target)
        sumL += loss.item()
    print('Before: \tLoss: {:.6f}'.format(sumL))

    # run the main training loop
    for epoch in range(epochs):
        sumL = 0
        for i in range(len(dataset_train)):
            net_out = net(dataset_train[i][0])
            target = dataset_train[i][1]
            optimizer.zero_grad()
            # print("net res=",net_out)
            # print("target=",target)
            loss = criterion(net_out, target)
            loss.backward()
            optimizer.step()
            sumL += loss.item()
        print('Train Epoch: {:.0f}\tLoss: {:.6f}'.format(epoch, sumL / len(dataset_train)))

    # run a test loop
    test_loss = 0
    correct = 0
    print(len(dataset_test))
    pic_test = plt.figure(figsize=(32, 64))
    j = 0
    size_pic = 2
    size_x = size_pic
    size_y = size_pic
    k = 0
    with torch.no_grad():
        for i in range(len(dataset_test)):
            net_out = net(dataset_test[i][0])
            target = dataset_test[i][1]
            test_loss += criterion(net_out, target).item()
            j += 2;
            paint_cells(target, net_out, k)
            k += 1
        test_loss /= len(dataset_test)
        print('\nTest set: Average loss: {:.4f}\n'.format(test_loss))
        plt.show()


def paint_cells(target, net_out, k):
    xmin = 0
    xmax = 1000
    ymin = -500
    ymax = 500
    zmin = -500
    zmax = 0
    nx = 10
    nz = 5
    hx = (xmax - xmin) / nx
    hz = (zmax - zmin) / nz
    f, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title("target")
    ax1.imshow(target.reshape(5, 10))
    ax2.set_title('net_out')
    ax2.imshow(net_out.reshape(5, 10))
    filename = 'result/fig' + '_' + str(k) + '.png'
    plt.savefig(filename)
    plt.close(f)


if __name__ == "__main__":
    # dataset = read_dataset()
    dataset_size = 100
    # model_path = "models/model_100.pkl"
    dataset = []
    for i in range(dataset_size):
        mesh = read_mesh_from_file(f"../datasets/dataset_0/mesh_{i}.mes")
        receivers = read_receivers_from_file(f"../datasets/dataset_0/receivers_{i}.dat")
        px = torch.tensor([cell.p[0] for cell in mesh], dtype=torch.float32)
        Bz = torch.tensor([r.b[0] for r in receivers], dtype=torch.float32)
        dataset.append([Bz, px])
    n_train = int(len(dataset) * 0.8)
    print(n_train)
    print(len(dataset) - n_train)
    dataset_train, dataset_test = dataset[:n_train], dataset[n_train:]
    create_nn(dataset_train, dataset_test)
