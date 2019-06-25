#!/usr/bin/env python
# encoding: utf-8


import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import make_conv_layers

CNN8_CONFIG = [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M']

class CNN8(nn.Module):
  """ The class defining the CNN8 model.

  Attributes
  ----------
  num_classes: int
      The number of classes.
  drop_rate: float
      The probability for dropout.
  conv: :py:class:`torch.nn.Module`
    The output of the convolutional / maxpool layers
  avgpool: :py:class:`torch.nn.Module`
    The output of the average pooling layer (used as embedding) 
  classifier: :py:class:`torch.nn.Module`
    The output of the last linear (logits)

  """ 

  def __init__(self, num_cls, drop_rate=0.5):
    """ Init method

    Parameters
    ----------
    num_cls: int
        The number of classes.
    drop_rate: float
        The probability for dropout.

    """
    
    super(CNN8, self).__init__()
    self.num_classes = num_cls
    self.drop_rate = float(drop_rate)
    self.conv = make_conv_layers(CNN8_CONFIG)
    self.avgpool = nn.AvgPool2d(8)
    self.classifier = nn.Linear(512, self.num_classes)

  def forward(self, x):
    """ Propagate data through the network

    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      The data to forward through the network

    Returns
    -------
    x: :py:class:`torch.Tensor` 
      The last layer of the network
    
    """

    x = self.conv(x)
    x = self.avgpool(x)
    x = x.view(x.size(0), -1)
    x = F.dropout(x, p = self.drop_rate, training=self.training)
    out = self.classifier(x)
    return out, x # x for feature

