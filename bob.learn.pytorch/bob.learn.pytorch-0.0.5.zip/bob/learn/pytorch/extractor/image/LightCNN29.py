import numpy

import torch
from torch.autograd import Variable

import torchvision.transforms as transforms

from bob.learn.pytorch.architectures import LightCNN29
from bob.bio.base.extractor import Extractor

class LightCNN29Extractor(Extractor):
  """ The class implementing the feature extraction of LightCNN29 embeddings.

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
      The network architecture
  to_tensor: :py:mod:`torchvision.transforms`
      The transform from numpy.array to torch.Tensor
  norm: :py:mod:`torchvision.transforms`
      The transform to normalize the input 

  """
  
  def __init__(self, model_file=None, num_classes=79077):
    """ Init method

    Parameters
    ----------
    model_file: str
        The path of the trained network to load
    num_classes: int
        The number of classes.
    
    """
        
    Extractor.__init__(self, skip_extractor_training=True)
    
    # model
    self.network = LightCNN29(num_classes=num_classes)
    if model_file is None:
      # do nothing (used mainly for unit testing) 
      pass
    else:

      cp = torch.load(model_file, map_location='cpu')
      
      # checked if pre-trained model was saved using nn.DataParallel ...
      saved_with_nnDataParallel = False
      for k, v in cp['state_dict'].items():
        if 'module' in k:
          saved_with_nnDataParallel = True
          break

      # if it was, you have to rename the keys of state_dict ... (i.e. remove 'module.')
      if saved_with_nnDataParallel:
        if 'state_dict' in cp:
          from collections import OrderedDict
          new_state_dict = OrderedDict()
          for k, v in cp['state_dict'].items():
            name = k[7:]
            new_state_dict[name] = v
          self.network.load_state_dict(new_state_dict)
      else:
          self.network.load_state_dict(cp['state_dict'])
    self.network.eval()

    # image pre-processing
    self.to_tensor = transforms.ToTensor()
    self.norm = transforms.Normalize((0.5,), (0.5,))

  def __call__(self, image):
    """ Extract features from an image

    Parameters
    ----------
    image : 2D :py:class:`numpy.ndarray` (floats)
      The grayscale image to extract the features from. Its size must be 128x128

    Returns
    -------
    feature : :py:class:`numpy.ndarray` (floats)
      The extracted features as a 1d array of size 320 
    
    """
  
    # torchvision.transforms expect a numpy array of size HxWxC
    input_image = numpy.expand_dims(image, axis=2)
    input_image = self.to_tensor(input_image)
    input_image = self.norm(input_image)
    input_image = input_image.unsqueeze(0)
    
    # to be compliant with the loaded model, where weight and biases are torch.FloatTensor
    input_image = input_image.float()

    _ , features = self.network.forward(Variable(input_image))
    features = features.data.numpy().flatten()
    return features
