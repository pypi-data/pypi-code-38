import torch
from .utils import make_conv_layers

CASIA_CONFIG = [32, 64, 'M', 64, 128, 'M', 96, 192, 'M', 128, 256, 'M', 160, 320] 

class CASIANet(torch.nn.Module):
  """ The class defining the CASIA-Net CNN model.

  This class implements the CNN described in:
  "Learning Face Representation From Scratch", D. Yi, Z. Lei, S. Liao and S.z. Li, 2014

  Attributes
  ----------
  num_classes: int
    The number of classes.
  drop_rate: float
    The probability for dropout.
  conv: :py:class:`torch.nn.Module`
    The output of the convolutional / maxpool layers
  avgpool: :py:class:`torch.nn.Module`
    The output of the average pooling layer (used as embedding) 
  classifier: :py:class:`torch.nn.Module`
    The output of the last linear (logits)

  """ 

  def __init__(self, num_cls, drop_rate=0.5):
    """ Init method

    Parameters
    ----------
    num_cls: int
        The number of classes.
    drop_rate: float
        The probability for dropout.

    """
        
    super(CASIANet, self).__init__()
    self.num_classes = num_cls
    self.drop_rate = float(drop_rate)
    self.conv = make_conv_layers(CASIA_CONFIG)
    self.avgpool = torch.nn.AvgPool2d(8)
    self.classifier = torch.nn.Linear(320, self.num_classes)

  def forward(self, x):
    """ Propagate data through the network

    Parameters
    ----------
    x: :py:class:`torch.Tensor` 
      The data to forward through the network

    Returns
    -------
    x: :py:class:`torch.Tensor` 
      The last layer of the network
    
    """

    x = self.conv(x)
    x = self.avgpool(x)
    x = x.view(x.size(0), -1)
    x = torch.nn.functional.dropout(x, p = self.drop_rate, training=self.training)
    out = self.classifier(x)
    return out, x # x for feature
