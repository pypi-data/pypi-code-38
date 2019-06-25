import numpy as np 
import torch
from torch.autograd import Variable

import torchvision.transforms as transforms

from bob.learn.pytorch.architectures import MCDeepPixBiS
from bob.bio.base.extractor import Extractor

import logging
logger = logging.getLogger("bob.learn.pytorch")

class MCDeepPixBiSExtractor(Extractor):
  """ The class implementing the score computation for MCDeepPixBiS architecture.

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
    The network architecture
  transforms: :py:mod:`torchvision.transforms`
    The transform from numpy.array to torch.Tensor
  scoring_method: str
    The scoring method to be used to get the final score, 
    available methods are ['pixel_mean','binary','combined']. 

  """
  
  def __init__(self, transforms = transforms.Compose([transforms.ToTensor(),transforms.Normalize(mean=[0.5], std=[0.225])]), model_file=None, num_channels=8, scoring_method='pixel_mean'):

                                 
    """ Init method

    Parameters
    ----------
    model_file: str
      The path of the trained PAD network to load
    transforms: :py:mod:`torchvision.transforms` 
      Tranform to be applied on the image
    scoring_method: str
      The scoring method to be used to get the final score, 
      available methods are ['pixel_mean','binary','combined']. 
    
    """

    Extractor.__init__(self, skip_extractor_training=True)
    
    # model
    self.transforms = transforms 
    self.scoring_method = scoring_method
    self.num_channels =num_channels
    self.network = MCDeepPixBiS(pretrained=False, num_channels=self.num_channels)
    self.available_scoring_methods=['pixel_mean','binary','combined']

    logger.debug('Scoring method is : {}'.format(self.scoring_method.upper())) 

    if model_file is None:
      # do nothing (used mainly for unit testing) 
      logger.debug("No pretrained file provided")
      pass
    else:

      # With the new training
      logger.debug('Starting to load the pretrained PAD model')

      try:
        cp = torch.load(model_file)
      except:
        raise ValueError('Failed to load the model file : {}'.format(model_file))

      if 'state_dict' in cp:
        self.network.load_state_dict(cp['state_dict'])
      else:
        raise ValueError('Failed to load the state_dict for model file: {}'.format(model_file))

      logger.debug('Loaded the pretrained PAD model')    
 
    self.network.eval()

  def __call__(self, image):
    """ Extract features from an image

    Parameters
    ----------
    image : 3D :py:class:`numpy.ndarray`
      The image to extract the score from. Its size must be num_channelsx224x224;
      
    Returns
    -------
    output : float
      The extracted feature is a scalar values ~1 for bonafide and ~0 for PAs
    
    """
   
    input_image = np.rollaxis(np.rollaxis(image, 2),2) # changes to 224x224xnum_channels
    input_image = self.transforms(input_image)
    input_image = input_image.unsqueeze(0)
    
    output = self.network.forward(Variable(input_image))
    output_pixel = output[0].data.numpy().flatten()
    output_binary = output[1].data.numpy().flatten()

    if self.scoring_method=='pixel_mean':
      score=np.mean(output_pixel)
    elif self.scoring_method=='binary':
      score=np.mean(output_binary)
    elif self.scoring_method=='combined':
      score= (np.mean(output_pixel)+np.mean(output_binary))/2.0
    else:
      raise ValueError('Scoring method {} is not implemented.'.format(self.scoring_method))

    # output is a scalar score

    return np.reshape(score,(1,-1))
