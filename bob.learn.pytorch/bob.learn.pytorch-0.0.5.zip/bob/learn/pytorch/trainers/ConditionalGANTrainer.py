#!/usr/bin/env python
# encoding: utf-8


import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import torchvision.utils as vutils

import bob.core
logger = bob.core.log.setup("bob.learn.pytorch")

import time

class ConditionalGANTrainer(object):
  """Class to train a Conditional GAN

  Attributes
  ----------
  generator : :py:class:`torch.nn.Module`
    The generator network
  discriminator : :py:class:`torch.nn.Module`
    The discriminator network
  image_size: list of :obj:`int`
    The size of the images in this format: [channels,height, width]
  batch_size: int
    The size of your minibatch
  noise_dim: int
    The dimension of the noise (input to the generator)
  conditional_dim: int
    The dimension of the conditioning variable
  use_gpu: bool
    If you would like to use the gpu
  fixed_noise : :py:class:`torch.Tensor`
    The fixed input noise to the generator.
  fixed_one_hot : :py:class:`torch.Tensor`
    The set of fixed one-hot encoded conditioning variable 
  criterion : :py:class:`torch.nn.BCELoss`
    The binary cross-entropy loss
  
  """
  def __init__(self, netG, netD, image_size, batch_size=64, noise_dim=100, conditional_dim=13, use_gpu=False, verbosity_level=2):
    """Init function

    Parameters
    ----------
    netG : :py:class:`torch.nn.Module`
      The generator network
    netD : :py:class:`torch.nn.Module`
      The discriminator network
    image_size: list of :obj:`int`
      The size of the images in this format: [channels,height, width]
    batch_size: int
      The size of your minibatch
    noise_dim: int
      The dimension of the noise (input to the generator)
    conditional_dim: int
      The dimension of the conditioning variable
    use_gpu: bool
      If you would like to use the gpu
    verbosity_level: int
      The level of verbosity output to stdout
  
    """
    bob.core.log.set_verbosity_level(logger, verbosity_level)
    
    self.netG = netG
    self.netD = netD
    self.image_size = image_size
    self.batch_size = batch_size
    self.noise_dim = noise_dim 
    self.conditional_dim = conditional_dim 
    self.use_gpu = use_gpu

    # fixed conditional noise - used to generate samples (one for each value of the conditional variable)
    self.fixed_noise = torch.FloatTensor(self.conditional_dim, noise_dim, 1, 1).normal_(0, 1)
    self.fixed_one_hot = torch.FloatTensor(self.conditional_dim, self.conditional_dim, 1, 1).zero_()
    for k in range(self.conditional_dim):
      self.fixed_one_hot[k, k] = 1
    
    # TODO: figuring out the CPU/GPU thing - Guillaume HEUSCH, 17-11-2017
    self.fixed_noise = Variable(self.fixed_noise)
    self.fixed_one_hot = Variable(self.fixed_one_hot)

    # binary cross-entropy loss
    self.criterion = nn.BCELoss()

    # move stuff to GPU if needed
    if self.use_gpu:
      self.netD.cuda()
      self.netG.cuda()
      self.criterion.cuda()


  def train(self, dataloader, n_epochs=10, learning_rate=0.0002, beta1=0.5, output_dir='out'):
    """trains the Conditional GAN.

    Parameters
    ----------
    dataloader: :py:class:`torch.utils.data.DataLoader`
      The dataloader for your data
    n_epochs: int
      The number of epochs you would like to train for
    learning_rate: float
      The learning rate for Adam optimizer
    beta1: float
      The beta1 for Adam optimizer
    output_dir: str
      The directory where you would like to output images and models

    """
    real_label = 1
    fake_label = 0
    
    # setup optimizer
    optimizerD = optim.Adam(self.netD.parameters(), lr=learning_rate, betas=(beta1, 0.999))
    optimizerG = optim.Adam(self.netG.parameters(), lr=learning_rate, betas=(beta1, 0.999))
    
    for epoch in range(n_epochs):
      for i, data in enumerate(dataloader, 0):
     
        start = time.time()

        # get the data and pose labels
        real_images = data['image']
        poses = data['pose']

        # WARNING: the last batch could be smaller than the provided size
        batch_size = len(real_images)
       
        # create the Tensors with the right batch size
        noise = torch.FloatTensor(batch_size, self.noise_dim, 1, 1).normal_(0, 1)
        label = torch.FloatTensor(batch_size)

        # create the one hot conditional vector (generator) and feature maps (discriminator)
        one_hot_feature_maps = torch.FloatTensor(batch_size, self.conditional_dim, self.image_size[1], self.image_size[2]).zero_()
        one_hot_vector = torch.FloatTensor(batch_size, self.conditional_dim, 1, 1).zero_()
        for k in range(batch_size):
          one_hot_feature_maps[k, poses[k], :, :] = 1
          one_hot_vector[k, poses[k]] = 1
        
        # move stuff to GPU if needed
        if self.use_gpu:
          real_images = real_images.cuda()
          label = label.cuda()
          noise = noise.cuda()
          one_hot_feature_maps = one_hot_feature_maps.cuda() 
          one_hot_vector = one_hot_vector.cuda()

        # =============
        # DISCRIMINATOR 
        # =============
        self.netD.zero_grad()
     
        # === REAL DATA ===
        label.resize_(batch_size).fill_(real_label)
        imagev = Variable(real_images)
        one_hot_fmv = Variable(one_hot_feature_maps)
        labelv = Variable(label)
        output_real = self.netD(imagev, one_hot_fmv)
        errD_real = self.criterion(output_real, labelv)
        errD_real.backward()

        # === FAKE DATA ===
        noisev = Variable(noise)
        one_hot_vv = Variable(one_hot_vector)
        fake = self.netG(noisev, one_hot_vv)
        labelv = Variable(label.fill_(fake_label))
        output_fake = self.netD(fake, one_hot_fmv)
        errD_fake = self.criterion(output_fake, labelv)
        errD_fake.backward(retain_graph=True)
        
        # perform optimization (i.e. update discriminator parameters)
        errD = errD_real + errD_fake
        optimizerD.step()

        # =========
        # GENERATOR 
        # =========
        self.netG.zero_grad()
        labelv = Variable(label.fill_(real_label))  # fake labels are real for generator cost
        output_generated = self.netD(fake, one_hot_fmv)
        errG = self.criterion(output_generated, labelv)
        errG.backward()
        optimizerG.step()

        end = time.time()
        logger.info("[{}/{}][{}/{}] => Loss D = {} -- Loss G = {} (time spent: {})".format(epoch, n_epochs, i, len(dataloader), errD.item(), errG.item(), (end-start)))
        
      # save generated images at every epoch
      # TODO: model moved to CPU and back and I don't really know why (expected CPU tensor error)
      # To summarize:
      # tried to move tensors, variables on the GPU -> does not work
      # let the tensors on the CPU -> does not work
      # => model has to be brought back to the CPU :/
      if self.use_gpu:
        self.netG = self.netG.cpu()
      fake_examples = self.netG(self.fixed_noise, self.fixed_one_hot)
      if self.use_gpu:
        self.netG = self.netG.cuda()
      vutils.save_image(fake_examples.data, '%s/fake_samples_epoch_%03d.png' % (output_dir, epoch), normalize=True)

      # do checkpointing
      torch.save(self.netG.state_dict(), '%s/netG_epoch_%d.pth' % (output_dir, epoch))
      torch.save(self.netD.state_dict(), '%s/netD_epoch_%d.pth' % (output_dir, epoch))
