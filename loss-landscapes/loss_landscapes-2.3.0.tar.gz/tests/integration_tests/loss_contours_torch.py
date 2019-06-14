"""
Testing version of the code in examples/loss_contours
"""

import copy
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn
import torch.optim as optim
import torchvision.datasets as datasets
from tqdm import tqdm
import loss_landscapes
import model_metrics.torch.sl_metrics as sl_evaluators
import model_metrics.torch.misc_metrics as misc_evaluators
from tests.testing_utils.models_torch import MLP
from tests.testing_utils.functions_torch import Flatten

# constants
IN_DIM = 28 * 28
OUT_DIM = 10
LR = 10 ** -2
BATCH_SIZE = 512
EPOCHS = 0
STEPS = 40


def train(model, optimizer, criterion, train_loader, epochs):
    """ Trains the given model with the given optimizer, loss function, etc. """
    model.train()
    # train model
    for _ in tqdm(range(epochs), 'Training'):
        for count, batch in enumerate(train_loader, 0):
            optimizer.zero_grad()
            x, y = batch

            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

    model.eval()


def main():
    # download MNIST and setup data loaders
    mnist_train = datasets.MNIST(root='./data', train=True, download=True, transform=Flatten())
    train_loader = torch.utils.data.DataLoader(mnist_train, batch_size=BATCH_SIZE, shuffle=False)
    mnist_test = datasets.MNIST(root='./data', train=False, download=True, transform=Flatten())
    test_loader = torch.utils.data.DataLoader(mnist_test, batch_size=10000, shuffle=False)

    # setup evaluator for classification accurary
    x_test, y_test = iter(test_loader).__next__()
    test_evaluator = misc_evaluators.ClassificationAccuracyEvaluator(x_test, y_test)

    # define model and deepcopy initial model
    model = MLP(IN_DIM, OUT_DIM, dropout=0.01)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    criterion = torch.nn.CrossEntropyLoss()
    model_initial = copy.deepcopy(model)

    print('Accuracy: ' + str(loss_landscapes.point(model_initial, test_evaluator)) + '\n')

    train(model, optimizer, criterion, train_loader, EPOCHS)

    # deepcopy final model and prepare for loss evaluation
    model_final = copy.deepcopy(model)
    print('Accuracy: ' + str(loss_landscapes.point(model_final, test_evaluator)) + '\n')
    x, y = iter(train_loader).__next__()
    loss_evaluator = sl_evaluators.LossEvaluator(criterion, x, y)

    # 2D contour plot of loss
    loss_data = loss_landscapes.random_plane(model_final, loss_evaluator, distance=1, steps=STEPS, normalization='layer')
    plt.contour(loss_data, levels=50)
    plt.title('Loss Contours around Trained Model')
    plt.savefig(fname='contour.png', dpi=250)

    # 3D surface of loss
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    X = np.array([[j for j in range(STEPS)] for i in range(STEPS)])
    Y = np.array([[i for _ in range(STEPS)] for i in range(STEPS)])
    ax.plot_surface(X, Y, loss_data, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
    ax.set_title('Surface Plot of Loss Landscape')
    fig.savefig(fname='3d-contour.png', dpi=250)


if __name__ == '__main__':
    main()
