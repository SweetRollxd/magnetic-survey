import numpy as np
# from numpy import random
import random
from extras.custom_functions import read_mesh_from_file, read_receivers_from_file


def relu(x: np.ndarray, derivative: bool = False):
    if derivative:
        # return np.ones(x.shape) if x >= 0 else np.zeros(x.shape)
        return (x > 0) * 1
    return np.maximum(0, x)
    # return np.array([max(0, val) for val in x])


def sigmoid(x, derivative: bool = False):
    if derivative:
        return x * (1 - x)
    return 1 / (1 + np.exp(-x))


def tanh(x, derivative: bool = False):
    if derivative:
        return 1 - tanh(x) ** 2
    return 2 / (1 + np.exp(-2 * x)) - 1


class Network:
    def __init__(self, activation_func: str = "relu", hidden_layer_size: int = 10):
        # self.inputs = inputs
        self.weights1 = np.random.rand(120, hidden_layer_size)
        self.weights2 = np.random.rand(hidden_layer_size, 600)
        self.output = None
        self.hidden_layer = None
        self.inputs = None
        if activation_func == "relu":
            self.activation_func = relu
        elif activation_func == "sigmoid":
            self.activation_func = sigmoid
        elif activation_func == "tanh":
            self.activation_func = tanh

    def feedforward(self, inputs):
        self.inputs = inputs
        self.hidden_layer = self.activation_func(np.dot(self.inputs, self.weights1))
        self.output = self.activation_func(np.dot(self.hidden_layer, self.weights2))
        # print(f"Output = {self.output}")

    def backpropagation(self, y):
        # layer_3_delta = (l3 - input_y) * (l3 * (1 - l3))
        # layer_2_delta = layer_3_delta.dot(syn2.T) * (l2 * (1 - l2))
        # layer_1_delta = layer_2_delta.dot(syn1.T) * (l1 * (1 - l1))

        dw2 = self.mse(y, derivative=True) * self.activation_func(self.output, derivative=True)
        # d_weights2 = np.dot(self.hidden_layer.T, (self.mse(y, derivative=True) * sigmoid(self.output, derivative=True)))
        d_weights2 = np.dot(self.hidden_layer.T, dw2)
        # d_weights2 = self.hidden_layer.T.dot(dw2)
        # d_weights1 = np.dot(self.inputs.T,  (np.dot(self.mse(y, derivative=True) * sigmoid(self.output, derivative=True), self.weights2.T) * sigmoid(self.hidden_layer,derivative=True)))
        # mse_sig = np.dot(mse, sig)
        dw1 = np.dot(dw2, self.weights2.T) * self.activation_func(self.hidden_layer, derivative=True)
        # sig_sig = np.dot(sig_weights, sigmoid(self.hidden_layer, derivative=True))
        d_weights1 = np.dot(self.inputs.T, dw1)

        alpha = 0.01
        # update the weights with the derivative (slope) of the loss function
        self.weights1 += alpha * d_weights1
        self.weights2 += alpha * d_weights2
        # pass

    def mse(self, y, derivative=False):
        if derivative:
            return 2 * (y - self.output)
        return (self.output - y) ** 2

    def train(self, inputs, outputs, epoch=1):
        for e in range(epoch):
            # print(f"Inputs = {inputs}")
            self.feedforward(inputs)
            # err = self.mse(outputs)
            # print(f"Error = {err.mean()}")
            self.backpropagation(outputs)
            # err = self.mse(outputs)
            # print(f"Error = {err.mean()}")

    def train_ds(self, x, y, epoch=1, batch_size=40):
        if len(x) != len(y):
            raise ValueError("Size of input and output arrays in not equal")
        errors = []
        for e in range(epoch):
            random_indexes = [random.randint(0, len(x)-1) for _ in range(batch_size)]
            print(f"Random indexes = {random_indexes}")
            batch_x = [x[ind] for ind in random_indexes]
            batch_y = [y[ind] for ind in random_indexes]
            # print(f"{}len)
            for i in range(len(random_indexes)):
                receiver_x = np.array([batch_x[i]])
                cell_y = np.array([batch_y[i]])
                self.feedforward(receiver_x)
                err = self.mse(y).mean()
                errors.append(err)
                self.backpropagation(cell_y)

        return errors

    def predict(self):
        pass


if __name__ == '__main__':
    network = Network(activation_func="tanh", hidden_layer_size=50)
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

        # print(f"Size of input layer: {len(receiver_inputs)}")
        # print(f"Size of output: {len(cell_outputs)}")
        #
        # print(f"Input layer = {receiver_inputs}")
    err = network.train_ds(dataset_x, dataset_y, epoch=20)
    print(f"Len of err = {len(err)}")
    print(err)
    # network.t

