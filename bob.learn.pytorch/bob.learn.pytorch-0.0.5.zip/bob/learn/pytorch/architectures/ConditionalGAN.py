#!/usr/bin/env python
# encoding: utf-8

import torch
import torch.nn as nn

class ConditionalGAN_generator(nn.Module):
  """ Class implementating the conditional GAN generator

  This network is introduced in the following publication:
  Mehdi Mirza, Simon Osindero: "Conditional Generative Adversarial Nets"

  Attributes
  ----------
  ngpu : int
    The number of available GPU devices
  main : :py:class:`torch.nn.Sequential`
    The sequential container

  """
  def __init__(self, noise_dim, conditional_dim, channels=3, ngpu=1):
    """Init function

    Parameters
    ----------
    noise_dim : int
      The dimension of the noise 
    conditional_dim : int
      The dimension of the conditioning variable 
    channels : int
      The number of channels in the image 
    ngpu : int
      The number of available GPU devices

    """
    super(ConditionalGAN_generator, self).__init__()
    self.ngpu = ngpu
    self.conditional_dim = conditional_dim
    
    # output dimension
    ngf = 64

    self.main = nn.Sequential(
      # input is Z, going into a convolution
      nn.ConvTranspose2d((noise_dim + conditional_dim), ngf * 8, 4, 1, 0, bias=False),
      nn.BatchNorm2d(ngf * 8),
      nn.ReLU(True),
      # state size. (ngf*8) x 4 x 4
      nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf * 4),
      nn.ReLU(True),
      # state size. (ngf*4) x 8 x 8
      nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf * 2),
      nn.ReLU(True),
      # state size. (ngf*2) x 16 x 16
      nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf),
      nn.ReLU(True),
      # state size. (ngf) x 32 x 32
      nn.ConvTranspose2d(ngf, channels, 4, 2, 1, bias=False),
      nn.Tanh()
      # state size. (nc) x 64 x 64
    )

  def forward(self, z, y):
    """Forward function

    Parameters
    ----------
    z : :py:class: `torch.autograd.Variable`
      The minibatch of noise.
    y : :py:class: `torch.autograd.Variable`
      The conditional one hot encoded vector for the minibatch.
    
    Returns
    -------
    :py:class:`torch.Tensor`
      the output of the generator (i.e. an image)
    
    """
    generator_input = torch.cat((z, y), 1)
    #if isinstance(generator_input.data, torch.cuda.FloatTensor) and self.ngpu > 1:
    #  output = nn.parallel.data_parallel(self.main, generator_input, range(self.ngpu))
    #else:
    #  output = self.main(generator_input)
    
    # let's assume that we will never face the case where more than a GPU is used ...
    output = self.main(generator_input)
    return output


class ConditionalGAN_discriminator(nn.Module):
  """ Class implementating the conditional GAN discriminator

  Attributes
  ----------
  conditional_dim: int
    The dimension of the conditioning variable.
  channels: int
    The number of channels in the input image (default: 3).
  ngpu : int
    The number of available GPU devices
  main : :py:class:`torch.nn.Sequential`
    The sequential container

  """ 
  def __init__(self, conditional_dim, channels=3, ngpu=1):
    """Init function

    Parameters
    ----------
    conditional_dim: int
      The dimension of the conditioning variable.
    channels: int
      The number of channels in the input image (default: 3).
    ngpu : int
      The number of available GPU devices
   
    """
    super(ConditionalGAN_discriminator, self).__init__()
    self.conditional_dim = conditional_dim
    self.ngpu = ngpu
    
    # input dimension
    ndf = 64
    self.main = nn.Sequential(
      # input is (nc) x 64 x 64
      nn.Conv2d((channels + conditional_dim), ndf, 4, 2, 1, bias=False),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf) x 32 x 32
      nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 2),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*2) x 16 x 16
      nn.Conv2d(ndf * 2, ndf * 4, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 4),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*4) x 8 x 8
      nn.Conv2d(ndf * 4, ndf * 8, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 8),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*8) x 4 x 4
      nn.Conv2d(ndf * 8, 1, 4, 1, 0, bias=False),
      nn.Sigmoid()
    )
  

  def forward(self, images, y):
    """Forward function

    Parameters
    ----------
    images : :py:class: `torch.autograd.Variable`
      The minibatch of input images.
    y : :py:class: `torch.autograd.Variable`
      The corresponding conditional feature maps.
    
    Returns
    -------
    :py:class:`torch.Tensor`
      the output of the discriminator
    """
    input_discriminator = torch.cat((images, y), 1)
    #if isinstance(input_discriminator.data, torch.cuda.FloatTensor) and self.ngpu > 1:
    #  output = nn.parallel.data_parallel(self.main, input_discriminator, range(self.ngpu))
    #else:
    #  output = self.main(input_discriminator)
    
    # let's assume that we will never face the case where more than a GPU is used ...
    output = self.main(input_discriminator)
    return output.view(-1, 1).squeeze(1)
