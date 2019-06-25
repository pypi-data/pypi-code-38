#!/usr/bin/env python
# encoding: utf-8

import torch
import torch.nn as nn


class DCGAN_generator(nn.Module):
  """ Class implementating the generator part of the Deeply Convolutional GAN

  This network is introduced in the following publication:
  Alec Radford, Luke Metz, Soumith Chintala: "Unsupervised Representation 
  Learning with Deep Convolutional Generative Adversarial Networks", ICLR 2016

  and most of the code is based on:
  https://github.com/pytorch/examples/tree/master/dcgan

  Attributes
  ----------
    ngpu : int
      The number of available GPU devices

  """
  def __init__(self, ngpu):
    """Init function

    Parameters
    ----------
      ngpu : int
        The number of available GPU devices

    """
    super(DCGAN_generator, self).__init__()
    self.ngpu = ngpu
        
    # just to test - will soon be args
    nz = 100 # noise dimension
    ngf = 64 # number of features map on the first layer
    nc = 3 # number of channels

    self.main = nn.Sequential(
      # input is Z, going into a convolution
      nn.ConvTranspose2d(     nz, ngf * 8, 4, 1, 0, bias=False),
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
      nn.ConvTranspose2d(ngf * 2,     ngf, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf),
      nn.ReLU(True),
      # state size. (ngf) x 32 x 32
      nn.ConvTranspose2d(    ngf,      nc, 4, 2, 1, bias=False),
      nn.Tanh()
      # state size. (nc) x 64 x 64
    )

  def forward(self, input):
    """Forward function

    Parameters
    ----------
    input : :py:class:`torch.Tensor`
    
    Returns
    -------
    :py:class:`torch.Tensor`
      the output of the generator (i.e. an image)

    """
    #if isinstance(input.data, torch.cuda.FloatTensor) and self.ngpu > 1:
    #  output = nn.parallel.data_parallel(self.main, input, range(self.ngpu))
    #else:
    #  output = self.main(input)
    
    # let's assume that we will never face the case where more than a GPU is used ...
    output = self.main(input)
    return output


class DCGAN_discriminator(nn.Module):
  """ Class implementating the discriminator part of the Deeply Convolutional GAN

  This network is introduced in the following publication:
  Alec Radford, Luke Metz, Soumith Chintala: "Unsupervised Representation 
  Learning with Deep Convolutional Generative Adversarial Networks", ICLR 2016

  and most of the code is based on:
  https://github.com/pytorch/examples/tree/master/dcgan

  Attributes
  ----------
    ngpu : int
      The number of available GPU devices

  """
  def __init__(self, ngpu):
    """Init function

    Parameters
    ----------
      ngpu : int
        The number of available GPU devices

    """
    super(DCGAN_discriminator, self).__init__()
    self.ngpu = ngpu
        
        
    # just to test - will soon be args
    ndf = 64
    nc = 3
       
    self.main = nn.Sequential(
      # input is (nc) x 64 x 64
      nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
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

  def forward(self, input):
    """Forward function

    Parameters
    ----------
    input : :py:class:`torch.Tensor`
    
    Returns
    -------
    :py:class:`torch.Tensor`
      the output of the generator (i.e. an image)

    """
    #if isinstance(input.data, torch.cuda.FloatTensor) and self.ngpu > 1:
    #  output = nn.parallel.data_parallel(self.main, input, range(self.ngpu))
    #else:
    #  output = self.main(input)
    
    # let's assume that we will never face the case where more than a GPU is used ...
    output = self.main(input)

    return output.view(-1, 1).squeeze(1)
