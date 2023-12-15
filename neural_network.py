import numpy as np
# from numpy import random


def relu(x: np.ndarray, derivative: bool = False):
    if derivative:
        return 1 if x >= 0 else 0
    return max(0, x)


class Network:
    def __init__(self, hidden_layer_size: int = 10):
        # self.inputs = inputs
        self.weights1 = np.random.rand(40, hidden_layer_size)
        self.weights2 = np.random.rand(hidden_layer_size, 200)

    def feedforward(self, inputs):
        self.hidden_layer = relu(np.dot(inputs, self.weights1))
        self.output = relu(np.dot(self.hidden_layer, self.weights2))
        # pass

    def backpropagation(self, y):
        # application of the chain rule to find derivative of the loss function with respect to weights2 and weights1
        d_weights2 = np.dot(self.hidden_layer.T, (2*(y - self.output) * relu(self.output, derivative=True)))
        d_weights1 = np.dot(self.hidden_layer.T,  (np.dot(2*(y - self.output) * relu(self.output, derivative=True), self.weights2.T) * relu(self.hidden_layer,derivative=True)))

        # update the weights with the derivative (slope) of the loss function
        self.weights1 += d_weights1
        self.weights2 += d_weights2
        # pass

    def train(self, inputs, outputs):
        self.feedforward(inputs)
        self.backpropagation(outputs)
        pass

    def predict(self):
        pass
