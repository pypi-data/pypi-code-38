#!/usr/bin/env python
# encoding: utf-8


import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable


import bob.core
logger = bob.core.log.setup("bob.learn.pytorch")

import time
import os
import numpy

class CNNTrainer(object):
  """
  Class to train a CNN

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
    The network to train
  batch_size: int
    The size of your minibatch
  use_gpu: bool
    If you would like to use the gpu
  verbosity_level: int
    The level of verbosity output to stdout
  
  """
 
  def __init__(self, network, batch_size=64, use_gpu=False, verbosity_level=2, num_classes=2):
    """ Init function

    Parameters
    ----------
    network: :py:class:`torch.nn.Module`
      The network to train
    batch_size: int
      The size of your minibatch
    use_gpu: bool
      If you would like to use the gpu
    verbosity_level: int
      The level of verbosity output to stdout
    num_classes: int
      The number of classes 

    """
    self.network = network
    self.num_classes = num_classes
    self.batch_size = batch_size
    self.use_gpu = use_gpu
    self.criterion = nn.CrossEntropyLoss()

    if self.use_gpu:
      self.network.cuda()

    bob.core.log.set_verbosity_level(logger, verbosity_level)

  def load_and_initialize_model(self, model_filename):
    """ Loads and initialize a model

    Parameters
    ----------
      model_filename: str

    """
    try:
      cp = torch.load(model_filename)
      logger.info("model {} loaded".format(model_filename))
    except RuntimeError:
      # pre-trained model was probably saved using nn.DataParallel ...
      cp = torch.load(model_filename, map_location='cpu')
      logger.info("model {} loaded on CPU".format(model_filename))
    
    if 'state_dict' in cp:
      from collections import OrderedDict
      new_state_dict = OrderedDict()
      for k, v in cp['state_dict'].items():
        name = k[7:]
        new_state_dict[name] = v
    cp['state_dict'] = new_state_dict

    logger.info("state_dict modified")
    ###########################################################################################################
    ### for each defined architecture, get the output size in pre-trained model, and change it if necessary ###

    # LightCNN
    if isinstance(self.network, bob.learn.pytorch.architectures.LightCNN.LightCNN9) \
      or isinstance(self.network, bob.learn.pytorch.architectures.LightCNN.LightCNN29) \
      or isinstance(self.network, bob.learn.pytorch.architectures.LightCNN.LightCNN29v2):
     
      last_layer_weight = 'fc2.weight'
      last_layer_bias = 'fc2.bias'

      num_classes_pretrained = cp['state_dict'][last_layer_weight].shape[0]
      
      if num_classes_pretrained == self.num_classes:
        self.network.load_state_dict(cp['state_dict'])
      else:
        var = 1.0 / (cp['state_dict'][last_layer_weight].shape[0])
        np_weights =  numpy.random.normal(loc=0.0, scale=var, size=((self.num_classes+1), cp['state_dict'][last_layer_weight].shape[1]))
        cp['state_dict'][last_layer_weight] = torch.from_numpy(np_weights)
        if not (isinstance(self.network, bob.learn.pytorch.architectures.LightCNN.LightCNN29v2)):
          cp['state_dict'][last_layer_bias] = torch.zeros(((self.num_classes+1),))
        self.network.load_state_dict(cp['state_dict'], strict=True)
      logger.info("state_dict loaded for {} with {} classes".format(type(self.network), self.num_classes))

    # CNN8
    if isinstance(self.network, bob.learn.pytorch.architectures.CNN8):
      
      num_classes_pretrained = cp['state_dict']['classifier.weight'].shape[0]
      if num_classes_pretrained == self.num_classes:
        self.network.load_state_dict(cp['state_dict'])
      else:
        var = 1.0 / (cp['state_dict']['classifier.weight'].shape[0])
        np_weights =  numpy.random.normal(loc=0.0, scale=var, size=((self.num_classes+1), cp['state_dict']['classifier.weight'].shape[1]))
        cp['state_dict']['classifier.weight'] = torch.from_numpy(np_weights)
        cp['state_dict']['classifier.bias'] = torch.zeros(((self.num_classes+1),))
        #self.network.load_state_dict(cp['state_dict'], strict=False)
        self.network.load_state_dict(cp['state_dict'], strict=True)
      logger.info("state_dict loaded for {} with {} classes".format(type(self.network), self.num_classes))

    # CASIANet
    if isinstance(self.network, bob.learn.pytorch.architectures.CASIANet):
      
      num_classes_pretrained = cp['state_dict']['classifier.weight'].shape[0]
      if num_classes_pretrained == self.num_classes:
        self.network.load_state_dict(cp['state_dict'])
      else:
        var = 1.0 / (cp['state_dict']['classifier.weight'].shape[0])
        np_weights =  numpy.random.normal(loc=0.0, scale=var, size=((self.num_classes+1), cp['state_dict']['classifier.weight'].shape[1]))
        cp['state_dict']['classifier.weight'] = torch.from_numpy(np_weights)
        cp['state_dict']['classifier.bias'] = torch.zeros(((self.num_classes+1),))
        #self.network.load_state_dict(cp['state_dict'], strict=False)
        self.network.load_state_dict(cp['state_dict'], strict=True)
      logger.info("state_dict loaded for {} with {} classes".format(type(self.network), self.num_classes))

    ###########################################################################################################

    start_epoch = 0
    start_iter = 0
    losses = []
    if 'epoch' in cp.keys():
      start_epoch = cp['epoch']
    if 'iteration' in cp.keys():
      start_iter = cp['iteration']
    if 'losses' in cp.keys():
      losses = cp['epoch']
  
    return start_epoch, start_iter, losses


  def save_model(self, output_dir, epoch=0, iteration=0, losses=None):
    """Save the trained network

    Parameters
    ----------
    output_dir: str
      The directory to write the models to
    epoch: int
      the current epoch
    iteration: int
      the current (last) iteration
    losses: list(float)
        The list of losses since the beginning of training 
    
    """ 
    
    saved_filename = 'model_{}_{}.pth'.format(epoch, iteration)    
    saved_path = os.path.join(output_dir, saved_filename)    
    logger.info('Saving model to {}'.format(saved_path))
    cp = {'epoch': epoch, 
          'iteration': iteration,
          'loss': losses, 
          'state_dict': self.network.cpu().state_dict()
          }
    torch.save(cp, saved_path)
    
    # moved the model back to GPU if needed
    if self.use_gpu :
        self.network.cuda()


  def train(self, dataloader, n_epochs=20, learning_rate=0.01, output_dir='out', model=None):
    """Performs the training.

    Parameters
    ----------
    dataloader: :py:class:`torch.utils.data.DataLoader`
      The dataloader for your data
    n_epochs: int
      The number of epochs you would like to train for
    learning_rate: float
      The learning rate for SGD optimizer.
    output_dir: str
      The directory where you would like to save models 
    
    """
    
    # if model exists, load it
    if model is not None:
      
      start_epoch, start_iter, losses = self.load_and_initialize_model(model)
      if start_epoch != 0: 
        logger.info('Previous network was trained up to epoch {}, iteration {}'.format(start_epoch, start_iter))
        if losses:
          logger.info('Last loss = {}'.format(losses[-1]))
      else: 
        logger.info('Starting training / fine-tuning from pre-trained model')

    else:
      start_epoch = 0
      start_iter = 0
      losses = []
      logger.info('Starting training from scratch')

    # setup optimizer
    optimizer = optim.SGD(self.network.parameters(), learning_rate, momentum = 0.9, weight_decay = 0.0005)

    # let's go
    for epoch in range(start_epoch, n_epochs):
      for i, data in enumerate(dataloader, 0):
   
        if i >= start_iter:
        
          start = time.time()
          
          images = data['image']
          labels = data['label']
          batch_size = len(images)
          if self.use_gpu:
            images = images.cuda()
            labels = labels.cuda()
          imagesv = Variable(images)
          labelsv = Variable(labels)

          output, _ = self.network(imagesv)
          loss = self.criterion(output, labelsv)
          optimizer.zero_grad()
          loss.backward()
          optimizer.step()

          end = time.time()
          logger.info("[{}/{}][{}/{}] => Loss = {} (time spent: {})".format(epoch, n_epochs, i, len(dataloader), loss.item(), (end-start)))
          losses.append(loss.item())
      
      # do stuff - like saving models
      logger.info("EPOCH {} DONE".format(epoch+1))
      self.save_model(output_dir, epoch=(epoch+1), iteration=0, losses=losses)
