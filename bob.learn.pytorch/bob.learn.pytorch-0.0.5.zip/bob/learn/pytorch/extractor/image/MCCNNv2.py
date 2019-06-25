import numpy as np 
import torch
from torch.autograd import Variable

import torchvision.transforms as transforms

from bob.learn.pytorch.architectures import MCCNNv2
from bob.bio.base.extractor import Extractor

import logging
logger = logging.getLogger("bob.learn.pytorch")

class MCCNNv2Extractor(Extractor):
  """ The class implementing the MC-CNN score computation.

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
      The network architecture
  transforms: :py:mod:`torchvision.transforms`
      The transform from numpy.array to torch.Tensor

  """
  
  def __init__(self, num_channels_used=4, adapted_layers = 'conv1-block1-group1-ffc', transforms = transforms.Compose([transforms.ToTensor()]), model_file=None):
    """ Init method

    Parameters
    ----------
    num_channels_used: int
      The number of channels to be used by the network. This could be 
      different from the number of channels present in the input image. For instance, 
      when used together with 'ChannelSelect' transform. The value of `num_channels_used`
      should be the number of channels eventually used by the network (i.e., output of transform).
    model_file: str
      The path of the trained PAD network to load
    transforms: :py:mod:`torchvision.transforms` 
      tranform to be applied on the image
    
    """

    Extractor.__init__(self, skip_extractor_training=True)
    
    # model
    self.transforms = transforms 
    self.network = MCCNNv2(num_channels=num_channels_used, adapted_layers=adapted_layers)

    logger.debug('Initiliazed model with lightCNN weights')
    
    #self.network=self.network.to(device)

    if model_file is None:
      # do nothing (used mainly for unit testing) 
      logger.debug("No pretrained file provided")
      pass
    else:


      # With the new training
      logger.debug('Starting to load the pretrained PAD model')
      cp = torch.load(model_file)
      if 'state_dict' in cp:
        self.network.load_state_dict(cp['state_dict'])

      logger.debug('Loaded the pretrained PAD model')    
 
    self.network.eval()

  def __call__(self, image):
    """ Extract features from an image

    Parameters
    ----------
    image : 3D :py:class:`numpy.ndarray` (floats)
      The multi-channel image to extract the score from. Its size must be num_channelsx128x128;
      Note: the value of `num_channels` is the number of channels as obtained from the preprocessed
      data. The actual number of channels used may vary, for instance
      if `ChannelSelect` transform is used, the number of channels used would change.
      
    Returns
    -------
    output : float
      The extracted feature is a scalar values ~1 for bonafide and ~0 for PAs
    
    """
   
    input_image = np.rollaxis(np.rollaxis(image, 2),2) # changes to 128x128xnum_channels
    input_image = self.transforms(input_image)
    input_image = input_image.unsqueeze(0)
    
    output = self.network.forward(Variable(input_image))
    output = output.data.numpy().flatten()

    # output is a scalar score

    return output