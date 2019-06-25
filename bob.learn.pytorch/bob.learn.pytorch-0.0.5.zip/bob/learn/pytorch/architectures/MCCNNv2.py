#!/usr/bin/env python
# encoding: utf-8

import torch
import torch.nn as nn
import torch.nn.functional as F

import os
import numpy as np

import pkg_resources 
import bob.extension.download

import bob.io.base

from .utils import MaxFeatureMap
from .utils import group
from .utils import resblock

import logging
logger = logging.getLogger("bob.learn.pytorch")

class MCCNNv2(nn.Module):
  """ The class defining the MCCNNv2 the difference from MCCNN is that it uses shared layers for
  layers which are not adapted. This avoids replicating shared layers.
  
  Attributes
  ----------
  num_channels: int
    The number of channels present in the input
  lcnn_layers: list
  	The adaptable layers present in the base LightCNN model
  module_dict: dict
  	A dictionary containing module names and `torch.nn.Module` elements as key, value pairs.
  layer_dict: :py:class:`torch.nn.ModuleDict`
  	Pytorch class containing the modules as a dictionary. 
  light_cnn_model_file: str
  	Absolute path to the pretrained LightCNN model file. 
  adapted_layers: str
    The layers to be adapted in training, they are to be separated by '-'. 
    Example: 'conv1-block1-group1-ffc'; 'ffc' denotes final fully connected layers which
    are adapted in all the cases. 
  url: str
  	The path to download the pretrained LightCNN model from.
  
  """
  def __init__(self, block=resblock, layers=[1, 2, 3, 4], num_channels=4, adapted_layers = 'conv1-block1-group1-ffc', verbosity_level=2):
    """ Init function

    Parameters
    ----------

    num_channels: int
      The number of channels present in the input
    adapted_layers: str
      The layers to be adapted in training, they are to be separated by '-'. 
      Example: 'conv1-block1-group1-ffc'; 'ffc' denotes final fully connected layers which
      are adapted in all the cases.
    verbosity_level: int
      Verbosity level.
    
    """
    super(MCCNNv2, self).__init__()

    self.num_channels=num_channels

    self.lcnn_layers=['conv1','block1','group1','block2', 'group2','block3','group3','block4','group4','fc']

    layers_present = self.lcnn_layers.copy()

    layers_present.append('ffc')

    # select the layers in the network to adapt

    adapted_layers_list=adapted_layers.split('-')

    assert('ffc' in adapted_layers_list)

    assert(set(adapted_layers_list)<=set(layers_present)) # to ensure layer names are valid

    self.shared_layers = list(set(layers_present) - set(adapted_layers_list)) # shared layers

    self.domain_specific_layers= list(set(adapted_layers_list)-set(['ffc']))

    logger.setLevel(verbosity_level)

    self.pool1  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.pool2  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.pool3  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)
    self.pool4  = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)

    # newly added FC layers

    self.linear1fc=nn.Linear(256*num_channels,10)
    self.linear2fc=nn.Linear(10,1)

    # add modules 

    module_dict={}

    for i in range(self.num_channels):

      m_dict={}

      m_dict['conv1']  = MaxFeatureMap(1, 48, 5, 1, 2)
      m_dict['block1'] = self._make_layer(block, layers[0], 48, 48)
      m_dict['group1'] = group(48, 96, 3, 1, 1)
      m_dict['block2'] = self._make_layer(block, layers[1], 96, 96)
      m_dict['group2'] = group(96, 192, 3, 1, 1)
      m_dict['block3'] = self._make_layer(block, layers[2], 192, 192)
      m_dict['group3'] = group(192, 128, 3, 1, 1)
      m_dict['block4'] = self._make_layer(block, layers[3], 128, 128)
      m_dict['group4'] = group(128, 128, 3, 1, 1)
      m_dict['fc']   = MaxFeatureMap(8*8*128, 256, type=0)

      # ch_0_should be the anchor 

      for layer in self.domain_specific_layers: # needs copies for domain specific layers

        layer_name="ch_{}_".format(i)+layer

        module_dict[layer_name] = m_dict[layer]

    m_dict={}

    m_dict['conv1']  = MaxFeatureMap(1, 48, 5, 1, 2)
    m_dict['block1'] = self._make_layer(block, layers[0], 48, 48)
    m_dict['group1'] = group(48, 96, 3, 1, 1)
    m_dict['block2'] = self._make_layer(block, layers[1], 96, 96)
    m_dict['group2'] = group(96, 192, 3, 1, 1)
    m_dict['block3'] = self._make_layer(block, layers[2], 192, 192)
    m_dict['group3'] = group(192, 128, 3, 1, 1)
    m_dict['block4'] = self._make_layer(block, layers[3], 128, 128)
    m_dict['group4'] = group(128, 128, 3, 1, 1)
    m_dict['fc']   = MaxFeatureMap(8*8*128, 256, type=0)

    for layer in self.shared_layers: # shared layers have ch_0_ prefix to make loading from pretrained model easier.

        layer_name="ch_0_"+layer

        module_dict[layer_name] = m_dict[layer]

    self.layer_dict = nn.ModuleDict(module_dict)

    # check for pretrained model 

    light_cnn_model_file = os.path.join(MCCNNv2.get_mccnnv2path(), "LightCNN_29Layers_checkpoint.pth.tar")

    url='http://www.idiap.ch/software/bob/data/bob/bob.learn.pytorch/master/LightCNN_29Layers_checkpoint.pth.tar'

    logger.info("Light_cnn_model_file path: {}".format(light_cnn_model_file))


    if not os.path.exists(light_cnn_model_file):

      bob.io.base.create_directories_safe(os.path.split(light_cnn_model_file)[0])

      logger.info('Downloading the LightCNN model')

      bob.extension.download.download_file(url,light_cnn_model_file)

      logger.info('Downloaded LightCNN model to location: {}'.format(light_cnn_model_file))


    ## Loding the pretrained model for ch_0

    self.load_state_dict(self.get_model_state_dict(light_cnn_model_file),strict=False)

    # copy over the weights to all other domain specific layers

    for layer in self.domain_specific_layers:

      for i in range(1, self.num_channels): # except for 0 th channel

        self.layer_dict["ch_{}_".format(i)+layer].load_state_dict(self.layer_dict["ch_0_"+layer].state_dict())  

            
  def _make_layer(self, block, num_blocks, in_channels, out_channels):
    """ makes multiple copies of the same base module

    Parameters
    ----------
    block: :py:class:`torch.nn.Module`
      The base block to replicate
    num_blocks: int
      Number of copies of the block to be made
    in_channels: int
      Number of input channels for a block
    out_channels: int
      Number of output channels for a block
    """
    layers = []
    for i in range(0, num_blocks):
        layers.append(block(in_channels, out_channels))
    return nn.Sequential(*layers)

  def forward(self, img):
    """ Propagate data through the network

    Parameters
    ----------
    img: :py:class:`torch.Tensor` 
      The data to forward through the network. Image of size num_channelsx128x128

    Returns
    -------
    output: :py:class:`torch.Tensor` 
      score 

    """
    
    embeddings=[]

    for i in range(self.num_channels):

      commom_layer = lambda x,y: x if self.lcnn_layers[y] in self.domain_specific_layers else 0

      # for ll in range(0,10):
      #   logger.debug("ch_{}_".format(commom_layer(i,ll))+self.lcnn_layers[ll])

      x=img[:,i,:,:].unsqueeze(1) # the image for the specific channel

      x = self.layer_dict["ch_{}_".format(commom_layer(i,0))+self.lcnn_layers[0]](x)
      x = self.pool1(x)

      x = self.layer_dict["ch_{}_".format(commom_layer(i,1))+self.lcnn_layers[1]](x)
      x = self.layer_dict["ch_{}_".format(commom_layer(i,2))+self.lcnn_layers[2]](x)
      x = self.pool2(x)

      x = self.layer_dict["ch_{}_".format(commom_layer(i,3))+self.lcnn_layers[3]](x)
      x = self.layer_dict["ch_{}_".format(commom_layer(i,4))+self.lcnn_layers[4]](x)
      x = self.pool3(x)

      x = self.layer_dict["ch_{}_".format(commom_layer(i,5))+self.lcnn_layers[5]](x)
      x = self.layer_dict["ch_{}_".format(commom_layer(i,6))+self.lcnn_layers[6]](x)
      x = self.layer_dict["ch_{}_".format(commom_layer(i,7))+self.lcnn_layers[7]](x)
      x = self.layer_dict["ch_{}_".format(commom_layer(i,8))+self.lcnn_layers[8]](x)
      x = self.pool4(x)

      x = x.view(x.size(0), -1)

      fc = self.layer_dict["ch_{}_".format(commom_layer(i,9))+self.lcnn_layers[9]](x)

      fc = F.dropout(fc, training=self.training)

      embeddings.append(fc)

    merged = torch.cat(embeddings, 1)

    output = self.linear1fc(merged)

    output = nn.Sigmoid()(output)

    output = self.linear2fc(output)

    output=nn.Sigmoid()(output)

    return output

  @staticmethod
  def get_mccnnv2path():

    import pkg_resources
    return pkg_resources.resource_filename('bob.learn.pytorch', 'models')


  def get_model_state_dict(self,pretrained_model_path):


    """ The class to load pretrained LightCNN model

    Attributes
    ----------
    pretrained_model_path: str
      Absolute path to the LightCNN model file

    new_state_dict: dict
      Dictionary with LightCNN weights

    """

    checkpoint = torch.load(pretrained_model_path,map_location=lambda storage,loc:storage)
    start_epoch = checkpoint['epoch']
    state_dict = checkpoint['state_dict']
    # create new OrderedDict that does not contain `module.`
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
      name = 'layer_dict.ch_0_'+k[7:] # remove `module.`
      new_state_dict[name] = v
    # load params
    return new_state_dict
