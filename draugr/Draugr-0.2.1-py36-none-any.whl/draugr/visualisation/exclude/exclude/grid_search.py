#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch

__author__ = 'cnheider'

import numpy as np
import pandas as pd

import pathlib

dataset_path = str(pathlib.Path.home() / 'Data' / 'Datasets' / 'DecisionSupportSystems' / 'Boston.csv')
dataset = pd.read_csv(dataset_path, index_col=0)

X = np.array(dataset.lstat).reshape(-1, 1)
y = dataset.medv


class Net(torch.nn.Module):
  def __init__(self, D_in, H, D_out):
    '''
    A feedForward neural network.
    Argurmets:
        n_feature: How many of features in your data
        n_hidden:  How many of neurons in the hidden layer
        n_output:  How many of neuros in the output leyar (defaut=1)
    '''
    super(Net, self).__init__()
    self.hidden = torch.nn.Linear(D_in, H, bias=True)  # hidden layer
    self.predict = torch.nn.Linear(H, D_out, bias=True)  # output layer
    self.n_feature, self.n_hidden, self.n_output = D_in, H, D_out

  def forward(self, x, **kwargs):
    '''
    Argurmets:
        x: Features to predict
    '''
    torch.nn.init.constant_(self.hidden.bias.data, 1)
    torch.nn.init.constant_(self.predict.bias.data, 1)
    x = torch.sigmoid(self.hidden(x))
    x = torch.sigmoid(self.predict(x))
    return x


from skorch import NeuralNetRegressor

X_trf = X
y_trf = y

net = NeuralNetRegressor(Net,
                         1, 2, 1,
                         max_epochs=100,
                         lr=0.001,
                         verbose=1)

from sklearn.model_selection import GridSearchCV

params = {
  'lr':        [0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3],
  'max_epochs':list(range(500, 5500, 500))
  }

gs = GridSearchCV(net, params, refit=False, scoring='r2', verbose=1, cv=10)

gs.fit(X_trf, y_trf)
