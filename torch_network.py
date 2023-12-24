import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

from extras.custom_functions import read_mesh_from_file, read_receivers_from_file


def split_dataset(ds, split_factor: float = 0.5):
    split_index = round(len(ds[0]) * split_factor)
    # print(split_index)
    return (ds[0][0:split_index], ds[1][0:split_index]), (ds[0][split_index:], ds[1][split_index:])


def create_nn(train, test, batch_size=200, learning_rate=0.01, epochs=10, hidden_layer_size: int = 200,
              log_interval=10):
    # train_loader = torch.utils.data.DataLoader(
    #     datasets.MNIST('../data', train=True, download=True,
    #                    transform=transforms.Compose([
    #                        transforms.ToTensor(),
    #                        transforms.Normalize((0.1307,), (0.3081,))
    #                    ])),
    #     batch_size=batch_size, shuffle=True)
    # test_loader = torch.utils.data.DataLoader(
    #     datasets.MNIST('../data', train=False, transform=transforms.Compose([
    #         transforms.ToTensor(),
    #         transforms.Normalize((0.1307,), (0.3081,))
    #     ])),
    #     batch_size=batch_size, shuffle=True)

    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.fc1 = nn.Linear(len(train[0][0]), hidden_layer_size)
            # self.fc2 = nn.Linear(200, 200)
            self.fc2 = nn.Linear(hidden_layer_size, len(train[1][0]))

        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            # x = F.tanh(self.fc1(x))
            # x = F.tanh(self.fc2(x))
            return x

    net = Net()
    print(net)

    # create a stochastic gradient descent optimizer
    optimizer = optim.SGD(net.parameters(), lr=learning_rate, momentum=0.9)
    # create a loss function
    criterion = nn.MSELoss()

    input_x, output_y = torch.tensor(train_ds[0]), torch.tensor(train_ds[1])

    # run the main training loop
    for epoch in range(epochs):
        # for batch_idx, (data, target) in enumerate(train_loader):
        err = 0
        for i in range(len(input_x)):

            data, target = Variable(input_x[i]), Variable(output_y[i])
            # resize data from (batch_size, 1, 28, 28) to (batch_size, 28*28)
            # data = data.view(-1, 28 * 28)
            optimizer.zero_grad()
            net_out = net(data)
            loss = criterion(net_out, target)
            loss.backward()
            optimizer.step()
            err += loss.data

            # if i % log_interval == 0:
            if i == len(input_x) - 1:
                print(f'Train Epoch: {epoch} [{i}/{len(train_ds[0])}] \tLoss: {loss.data}')
            #     print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
            #         epoch, batch_idx * len(data), len(train_loader.dataset),
            #                100 * batch_idx / len(train_loader), loss.data))
        print(f"Mean loss: {err / len(input_x)}")
                # run a test loop
    test_loss = 0
    correct = 0
    # for data, target in test_loader:
    input_x, output_y = torch.tensor(test_ds[0]), torch.tensor(test_ds[1])
    with torch.no_grad():
        for i in range(len(input_x)):
            data, target = Variable(input_x[i]), Variable(output_y[i])
            # data = data.view(-1, 28 * 28)
            net_out = net(data)
            # sum up batch loss
            # test_loss += criterion(net_out, target).data[0]
            test_loss += criterion(net_out, target).data
            # pred = net_out.data.max(1)[1]  # get the index of the max log-probability
            pred = net_out.data
            correct += pred.eq(target.data).sum()

        # test_loss /= len(test_loader.dataset)
        test_loss /= len(input_x)
        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(input_x) * 600,
            100. * correct / (len(input_x) * 600)))


if __name__ == "__main__":
    run_opt = 2
    dataset_x = []
    dataset_y = []
    dateset_size = 100
    for i in range(dateset_size):
        mesh = read_mesh_from_file(f"./datasets/dataset_0/mesh_{i}.mes")
        receivers = read_receivers_from_file(f"datasets/dataset_0/receivers_{i}.dat")

        receiver_inputs = [b for r in receivers for b in r.b]
        cell_outputs = [p for cell in mesh for p in cell.p]

        dataset_x.append(receiver_inputs)
        dataset_y.append(cell_outputs)

    dataset = (dataset_x, dataset_y)
    train_ds, test_ds = split_dataset(dataset, split_factor=0.8)
    # print(f"Train dataset = {train_ds}")
    # print(f"Test dataset = {test_ds}")
    # print(f"Len of train: {len(train_ds)}, test: {len(test_ds)}")
    # create_nn(dataset_x, dataset_y, dataset_x[0:2], dataset_y[0:2], epochs=100)
    create_nn(train_ds, test_ds, hidden_layer_size=200, epochs=100)
