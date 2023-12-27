import os
import random

import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from extras.custom_functions import read_mesh_from_file, read_receivers_from_file, write_mesh_to_file
from extras.generator import generate_mesh
from extras.point import Point


def split_dataset(ds, split_factor: float = 0.5):
    split_index = round(len(ds[0]) * split_factor)
    return (ds[0][0:split_index], ds[1][0:split_index]), (ds[0][split_index:], ds[1][split_index:])


random.seed(102)
torch.manual_seed(132)

class Net(nn.Module):
    def __init__(self, input_size: int, output_size: int, hidden_layer_size: int = 200):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_layer_size)
        # self.fc2 = nn.Linear(200, 200)
        self.fc2 = nn.Linear(hidden_layer_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # x = F.tanh(self.fc1(x))
        # x = F.tanh(self.fc2(x))

        return x


def train_network(net, train_ds, learning_rate=0.01, epochs=10):
    # create a stochastic gradient descent optimizer
    optimizer = optim.SGD(net.parameters(), lr=learning_rate, momentum=0.9)
    # create a loss function
    criterion = nn.MSELoss()

    input_x, output_y = torch.tensor(train_ds[0]), torch.tensor(train_ds[1])
    temp = list(zip(input_x, output_y))

    losses = []
    # run the main training loop
    for epoch in range(epochs):
        # for batch_idx, (data, target) in enumerate(train_loader):
        random.shuffle(temp)
        input_x, output_y = zip(*temp)
        err = 0
        for i in range(len(input_x)):

            data, target = Variable(input_x[i]), Variable(output_y[i])
            # data, target = input_x[i], output_y[i]
            optimizer.zero_grad()
            net_out = net(data)
            loss = criterion(net_out, target)
            loss.backward()
            optimizer.step()
            err += loss.item()

            if i == len(input_x) - 1:
                print(f'Train Epoch: {epoch} [{i}/{len(train_ds[0])}] \tLoss: {loss.item()}')
        print(f"Mean loss: {err / len(input_x)}")
        losses.append(err / len(input_x))
    return losses


def test_network(net, test_ds):
    # create a loss function
    criterion = nn.MSELoss()

    test_loss = 0
    correct = 0
    # for data, target in test_loader:
    input_x, output_y = torch.tensor(test_ds[0]), torch.tensor(test_ds[1])
    with torch.no_grad():
        for i in range(len(input_x)):
            data, target = Variable(input_x[i]), Variable(output_y[i])
            net_out = net(data)
            test_loss += criterion(net_out, target).data
            pred = net_out.data
            correct += pred.eq(target.data).sum()

        test_loss /= len(input_x)
        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(input_x) * len(output_y[0]),
            100. * correct / (len(input_x) * len(output_y[0]))))
    return test_loss


def predict(net, ds):
    return net(torch.tensor(ds))


def inverse_net_predict(receivers, mesh, model_path : str = "models/model_100.pkl"):
    magnetic = [b for r in receivers for b in r.b]
    # magnetic = [r.b[0] for r in receivers]
    net = torch.load(model_path)
    p = predict(net, magnetic)

    for i, c in enumerate(mesh):
        c.p = (p[i * 3].item(), p[i * 3 + 1].item(), p[i * 3 + 2].item())
        # c.p = (p[i].item(), 0, 0)
    return mesh


if __name__ == "__main__":
    dataset_x = []
    dataset_y = []
    dateset_size = 1000
    model_path = "models/model_100.pkl"
    dataset_name = "dataset_1"
    for i in range(dateset_size):
        mesh = read_mesh_from_file(f"./datasets/{dataset_name}/mesh_{i}.mes")
        receivers = read_receivers_from_file(f"datasets/{dataset_name}/receivers_{i}.dat")

        receiver_inputs = [b for r in receivers for b in r.b]
        cell_outputs = [p for cell in mesh for p in cell.p]
        # receiver_inputs = [r.b[0] for r in receivers]
        # cell_outputs = [cell.p[0] for cell in mesh]

        dataset_x.append(receiver_inputs)
        dataset_y.append(cell_outputs)

    dataset = (dataset_x, dataset_y)
    train_ds, test_ds = split_dataset(dataset, split_factor=0.8)
    network = Net(input_size=len(train_ds[0][0]), output_size=len(train_ds[1][0]), hidden_layer_size=len(train_ds[0][0])*2)
    losses = train_network(network, train_ds, epochs=100, learning_rate=0.01)

    with open("losses.txt", 'w') as f:
        f.writelines([str(l) + '\n' for l in losses])

    torch.save(network, model_path)

    test_network(network, test_ds)

    # Nx = 20
    # Nz = 10
    Nx = 10
    Nz = 5
    start_pnt = Point(0, -50, 0)
    end_pnt = Point(2000, 50, -1000)
    mesh = generate_mesh(start_pnt, end_pnt, count_x=Nx, count_y=1, count_z=Nz)

    receivers = read_receivers_from_file(f"datasets/dataset_1/receivers_1.dat")

    mesh = inverse_net_predict(receivers, mesh, model_path=model_path)
    print(mesh)
    write_mesh_to_file("datasets/results/result_0.mes", mesh)
    print('lol')
