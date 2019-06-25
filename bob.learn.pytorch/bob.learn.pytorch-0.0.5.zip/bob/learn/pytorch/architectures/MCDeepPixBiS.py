import torch
from torch import nn
from torchvision import models
import numpy as np


class MCDeepPixBiS(nn.Module):

    """ The class defining Multi-Channel Deep Pixelwise Binary Supervision for Face Presentation
    Attack Detection:

    This extends the following paper to multi-channel/ multi-spectral images with cross modal pretraining.

    Reference: Anjith George and Sébastien Marcel. "Deep Pixel-wise Binary Supervision for 
    Face Presentation Attack Detection." In 2019 International Conference on Biometrics (ICB).IEEE, 2019.

    The initialization uses `Cross modality pre-training` idea from the following paper:

    Wang L, Xiong Y, Wang Z, Qiao Y, Lin D, Tang X, Van Gool L. Temporal segment networks: 
    Towards good practices for deep action recognition. InEuropean conference on computer 
    vision 2016 Oct 8 (pp. 20-36). Springer, Cham.


    Attributes
    ----------
    pretrained: bool
        If set to `True` uses the pretrained DenseNet model as the base. If set to `False`, the network
        will be trained from scratch. 
        default: True 
    num_channels: int
        Number of channels in the input.      
    """

    def __init__(self, pretrained=True, num_channels=4):

        """ Init function

        Parameters
        ----------
        pretrained: bool
            If set to `True` uses the pretrained densenet model as the base. Else, it uses the default network
            default: True
        num_channels: int
            Number of channels in the input. 
        """
        super(MCDeepPixBiS, self).__init__()

        dense = models.densenet161(pretrained=pretrained)

        features = list(dense.features.children())

        temp_layer = features[0]

        # No bias in this architecture

        mean_weight = np.mean(temp_layer.weight.data.detach().numpy(),axis=1) # for 96 filters

        new_weight = np.zeros((96,num_channels,7,7))
  
        for i in range(num_channels):
            new_weight[:,i,:,:]=mean_weight

        features[0]=nn.Conv2d(num_channels, 96, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)

        features[0].weight.data = torch.Tensor(new_weight)

        self.enc = nn.Sequential(*features[0:8])

        self.dec=nn.Conv2d(384, 1, kernel_size=1, padding=0)

        self.linear=nn.Linear(14*14,1)


    def forward(self, x):
        """ Propagate data through the network

        Parameters
        ----------
        img: :py:class:`torch.Tensor` 
          The data to forward through the network. Expects Multi-channel images of size num_channelsx224x224

        Returns
        -------
        dec: :py:class:`torch.Tensor` 
            Binary map of size 1x14x14
        op: :py:class:`torch.Tensor`
            Final binary score.  

        """
        enc = self.enc(x)

        dec=self.dec(enc)

        dec=nn.Sigmoid()(dec)

        dec_flat=dec.view(-1,14*14)

        op=self.linear(dec_flat)

        op=nn.Sigmoid()(op)
 
        return dec,op
