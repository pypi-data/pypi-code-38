#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from torch import nn

class ConvAutoencoder(nn.Module):
  """
  A class defining a simple convolutional autoencoder.

  Attributes
  ----------
  return_latent_embedding : bool
    returns the encoder output if true, the reconstructed image otherwise.
  
  """
  def __init__(self, return_latent_embedding=False):
    """
    Init function
    
    Parameters
    ----------
    return_latent_embedding : bool
      returns the encoder output if true, the reconstructed image otherwise.
    """
        
    super(ConvAutoencoder, self).__init__()
    self.return_latent_embedding = return_latent_embedding

    self.encoder = nn.Sequential(nn.Conv2d(3, 16, 5, padding=2),
                                 nn.ReLU(True),
                                 nn.MaxPool2d(2),
                                 nn.Conv2d(16, 16, 5, padding=2),
                                 nn.ReLU(True),
                                 nn.MaxPool2d(2),
                                 nn.Conv2d(16, 16, 3, padding=2),
                                 nn.ReLU(True),
                                 nn.MaxPool2d(2),
                                 nn.Conv2d(16, 16, 3, padding=2),
                                 nn.ReLU(True),
                                 nn.MaxPool2d(2))

    self.decoder = nn.Sequential(nn.ConvTranspose2d(16, 16, 3, stride=2, padding=1),
                                 nn.ReLU(True),
                                 nn.ConvTranspose2d(16, 16, 3, stride=2, padding=1),
                                 nn.ReLU(True),
                                 nn.ConvTranspose2d(16, 16, 5, stride=2, padding=2),
                                 nn.ReLU(True),
                                 nn.ConvTranspose2d(16, 3, 5, stride=2, padding=2),
                                 nn.ReLU(True),
                                 nn.ConvTranspose2d(3, 3, 2, stride=1, padding=1),
                                 nn.Tanh())

  def forward(self, x):
    """ Propagate data through the network
    
    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      x = self.encoder(x)
    
    Returns
    -------
    :py:class:`torch.Tensor` 
      either the encoder output or the reconstructed image 
    
    """
    x = self.encoder(x)
    if self.return_latent_embedding:
      return x
    x = self.decoder(x)
    return x
