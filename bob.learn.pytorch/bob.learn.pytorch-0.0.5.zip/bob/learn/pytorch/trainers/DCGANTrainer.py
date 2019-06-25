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

class DCGANTrainer(object):
  """Class to train a DCGAN

  Attributes
  ----------
  netG : :py:class:`torch.nn.Module`
    The generator network
  netD : :py:class:`torch.nn.Module`
    The discriminator network
  batch_size: int
    The size of your minibatch
  noise_dim: int
    The dimension of the noise (input to the generator)
  use_gpu: bool
    If you would like to use the gpu
  input : :py:class:`torch.Tensor`
    The input image
  noise : :py:class:`torch.Tensor`
    The input noise to the generator
  fixed_noise : :py:class:`torch.Tensor`
    The fixed input noise to the generator.
    Used for generating images to save.
  label : :py:class:`torch.Tensor`
    label for real/fake images.
  criterion : :py:class:`torch.nn.BCELoss`
    The binary cross-entropy loss
  
  """
  def __init__(self, netG, netD, batch_size=64, noise_dim=100, use_gpu=False, verbosity_level=2):
    """Init function

    Parameters
    ----------
    generator : :py:class:`torch.nn.Module`
      The generator network
    discriminator : :py:class:`torch.nn.Module`
      The discriminator network
    batch_size: int
      The size of your minibatch
    noise_dim: int
      The dimension of the noise (input to the generator)
    use_gpu: bool
      If you would like to use the gpu
    verbosity_level: int
      The level of verbosity output to stdout

    """
    bob.core.log.set_verbosity_level(logger, verbosity_level)
    
    self.netG = netG
    self.netD = netD
    self.batch_size = batch_size
    self.noise_dim = noise_dim 
    self.use_gpu = use_gpu

    self.input = torch.FloatTensor(batch_size, 3, 64, 64)
    self.noise = torch.FloatTensor(batch_size, noise_dim, 1, 1)
    self.fixed_noise = torch.FloatTensor(batch_size, noise_dim, 1, 1).normal_(0, 1)
    self.label = torch.FloatTensor(batch_size)

    self.fixed_noise = Variable(self.fixed_noise)
    
    self.criterion = nn.BCELoss()

    if self.use_gpu:
      self.netD.cuda()
      self.netG.cuda()
      self.criterion.cuda()
      self.input, self.label = self.input.cuda(), self.label.cuda()
      self.noise, self.fixed_noise = self.noise.cuda(), self.fixed_noise.cuda()


  def train(self, dataloader, n_epochs=10, learning_rate=0.0002, beta1=0.5, output_dir='out'):
    """trains the DCGAN.

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

        # ===========================================================
        # (1) Update D network: maximize log(D(x)) + log(1 - D(G(z)))
        # ===========================================================
      
        # train with real
        self.netD.zero_grad()
        real_cpu = data['image']
        batch_size = real_cpu.size(0)
        if self.use_gpu:
          real_cpu = real_cpu.cuda()
        self.input.resize_as_(real_cpu).copy_(real_cpu)
        self.label.resize_(batch_size).fill_(real_label)
        inputv = Variable(self.input)
        labelv = Variable(self.label)

        output = self.netD(inputv)
        errD_real = self.criterion(output, labelv)
        errD_real.backward()
        D_x = output.data.mean()

        # train with fake
        self.noise.resize_(batch_size, self.noise_dim, 1, 1).normal_(0, 1)
        noisev = Variable(self.noise)
        fake = self.netG(noisev)
        labelv = Variable(self.label.fill_(fake_label))
        output = self.netD(fake.detach()) # detach() -> done for speed, not correctness (PyTorch github's issue says so ...)
        errD_fake = self.criterion(output, labelv)
        errD_fake.backward()
        D_G_z1 = output.data.mean()
        errD = errD_real + errD_fake
        optimizerD.step()

        # =========================================
        # (2) Update G network: maximize log(D(G(z)))
        # =========================================
        self.netG.zero_grad()
        labelv = Variable(self.label.fill_(real_label))  # fake labels are real for generator cost
        output = self.netD(fake)
        errG = self.criterion(output, labelv)
        errG.backward()
        D_G_z2 = output.data.mean()
        optimizerG.step()

        end = time.time()
        #logger.info("[{}/{}][{}/{}] => Loss D = {} -- Loss G = {} (time spent: {})".format(epoch, n_epochs, i, len(dataloader), errD.data[0], errG.data[0], (end-start)))
        logger.info("[{}/{}][{}/{}] => Loss D = {} -- Loss G = {} (time spent: {})".format(epoch, n_epochs, i, len(dataloader), errD.item(), errG.item(), (end-start)))
      
      # save generated images at every epoch
      fake = self.netG(self.fixed_noise)
      vutils.save_image(fake.data, '%s/fake_samples_epoch_%03d.png' % (output_dir, epoch), normalize=True)

      # do checkpointing
      torch.save(self.netG.state_dict(), '%s/netG_epoch_%d.pth' % (output_dir, epoch))
      torch.save(self.netD.state_dict(), '%s/netD_epoch_%d.pth' % (output_dir, epoch))
