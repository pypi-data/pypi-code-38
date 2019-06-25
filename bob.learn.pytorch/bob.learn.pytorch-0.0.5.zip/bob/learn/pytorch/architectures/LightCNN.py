#!/usr/bin/env python
# encoding: utf-8

import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import MaxFeatureMap
from .utils import group
from .utils import resblock

class LightCNN9(nn.Module):
  """ The class defining the light CNN with 9 layers

  This class implements the CNN described in:
  "A light CNN for deep face representation with noisy labels", Wu, Xiang and He, Ran and Sun, Zhenan and Tan, Tieniu,
  IEEE Transactions on Information Forensics and Security, vol 13, issue 11, 2018
  
  Attributes
  ----------
  features: :py:class:`torch.nn.Module`
    The output of the convolutional / max layers
  avgpool: :py:class:`torch.nn.Module`
    The output of the average pooling layer (used as embedding) 
  classifier: :py:class:`torch.nn.Module`
    The output of the last linear (logits)
 
  
  """

  def __init__(self, num_classes=79077):
    """ Init function

    Parameters
    ----------
    num_classes: int
      The number of classes.
    
    """
    super(LightCNN9, self).__init__()

    self.features = nn.Sequential(
        MaxFeatureMap(1, 48, 5, 1, 2), 
        nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True), 
        group(48, 96, 3, 1, 1), 
        nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True),
        group(96, 192, 3, 1, 1),
        nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True), 
        group(192, 128, 3, 1, 1),
        group(128, 128, 3, 1, 1),
        nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True),
        )
    self.fc1 = MaxFeatureMap(8*8*128, 256, type=0)
    self.fc2 = nn.Linear(256, num_classes)


  def forward(self, x):
    """ Propagate data through the network

    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      The data to forward through the network. Image of size 1x128x128

    Returns
    -------
    out: :py:class:`torch.Tensor` 
      class probabilities 
    x: :py:class:`torch.Tensor` 
      Output of the penultimate layer (i.e. embedding) 
    """
    x = self.features(x)
    x = x.view(x.size(0), -1)
    x = self.fc1(x)
    x = F.dropout(x, training=self.training)
    out = self.fc2(x)
    return out, x


class LightCNN29(nn.Module):
  """ The class defining the light CNN with 29 layers

  This class implements the CNN described in:
  "A light CNN for deep face representation with noisy labels", Wu, Xiang and He, Ran and Sun, Zhenan and Tan, Tieniu,
  IEEE Transactions on Information Forensics and Security, vol 13, issue 11, 2018
  
  Attributes
  ----------
  
  """
  def __init__(self, block=resblock, layers=[1, 2, 3, 4], num_classes=79077):
    """ Init function

    Parameters
    ----------
    num_classes: int
      The number of classes.
    
    """
    super(LightCNN29, self).__init__()

    self.conv1  = MaxFeatureMap(1, 48, 5, 1, 2)
    self.pool1  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.block1 = self._make_layer(block, layers[0], 48, 48)
    self.group1 = group(48, 96, 3, 1, 1)
    self.pool2  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.block2 = self._make_layer(block, layers[1], 96, 96)
    self.group2 = group(96, 192, 3, 1, 1)
    self.pool3  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.block3 = self._make_layer(block, layers[2], 192, 192)
    self.group3 = group(192, 128, 3, 1, 1)
    self.block4 = self._make_layer(block, layers[3], 128, 128)
    self.group4 = group(128, 128, 3, 1, 1)
    self.pool4  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.fc     = MaxFeatureMap(8*8*128, 256, type=0)
    self.fc2    = nn.Linear(256, num_classes)
            
  def _make_layer(self, block, num_blocks, in_channels, out_channels):
    """

    Parameters
    ----------
    
    """
    layers = []
    for i in range(0, num_blocks):
        layers.append(block(in_channels, out_channels))
    return nn.Sequential(*layers)

  def forward(self, x):
    """ Propagate data through the network

    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      The data to forward through the network. Image of size 1x128x128

    Returns
    -------
    out: :py:class:`torch.Tensor` 
      class probabilities 
    x: :py:class:`torch.Tensor` 
      Output of the penultimate layer (i.e. embedding) 
    """
    x = self.conv1(x)
    x = self.pool1(x)

    x = self.block1(x)
    x = self.group1(x)
    x = self.pool2(x)

    x = self.block2(x)
    x = self.group2(x)
    x = self.pool3(x)

    x = self.block3(x)
    x = self.group3(x)
    x = self.block4(x)
    x = self.group4(x)
    x = self.pool4(x)

    x = x.view(x.size(0), -1)
    fc = self.fc(x)
    fc = F.dropout(fc, training=self.training)
    out = self.fc2(fc)
    return out, fc


class LightCNN29v2(nn.Module):
  """ The class defining the light CNN with 29 layers (version 2)

  This class implements the CNN described in:
  "A light CNN for deep face representation with noisy labels", Wu, Xiang and He, Ran and Sun, Zhenan and Tan, Tieniu,
  IEEE Transactions on Information Forensics and Security, vol 13, issue 11, 2018
  
  Attributes
  ----------
  
  """
  def __init__(self, block=resblock, layers=[1, 2, 3, 4], num_classes=79077):
    """ Init function

    Parameters
    ----------
    num_classes: int
      The number of classes.
    
    """
    super(LightCNN29v2, self).__init__()
    self.conv1    = MaxFeatureMap(1, 48, 5, 1, 2)
    self.block1   = self._make_layer(block, layers[0], 48, 48)
    self.group1   = group(48, 96, 3, 1, 1)
    self.block2   = self._make_layer(block, layers[1], 96, 96)
    self.group2   = group(96, 192, 3, 1, 1)
    self.block3   = self._make_layer(block, layers[2], 192, 192)
    self.group3   = group(192, 128, 3, 1, 1)
    self.block4   = self._make_layer(block, layers[3], 128, 128)
    self.group4   = group(128, 128, 3, 1, 1)
    self.fc       = nn.Linear(8*8*128, 256)
    self.fc2      = nn.Linear(256, num_classes, bias=False)
            
  def _make_layer(self, block, num_blocks, in_channels, out_channels):
    """

    Parameters
    ----------
    
    """
    layers = []
    for i in range(0, num_blocks):
      layers.append(block(in_channels, out_channels))
    return nn.Sequential(*layers)

  def forward(self, x):
    """ Propagate data through the network

    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      The data to forward through the network. Image of size 1x128x128

    Returns
    -------
    out: :py:class:`torch.Tensor` 
      class probabilities 
    x: :py:class:`torch.Tensor` 
      Output of the penultimate layer (i.e. embedding) 
    """
    x = self.conv1(x)
    x = F.max_pool2d(x, 2) + F.avg_pool2d(x, 2)

    x = self.block1(x)
    x = self.group1(x)
    x = F.max_pool2d(x, 2) + F.avg_pool2d(x, 2)

    x = self.block2(x)
    x = self.group2(x)
    x = F.max_pool2d(x, 2) + F.avg_pool2d(x, 2)

    x = self.block3(x)
    x = self.group3(x)
    x = self.block4(x)
    x = self.group4(x)
    x = F.max_pool2d(x, 2) + F.avg_pool2d(x, 2)

    x = x.view(x.size(0), -1)
    fc = self.fc(x)
    x = F.dropout(fc, training=self.training)
    out = self.fc2(x)
    return out, fc
