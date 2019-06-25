from .CNN8 import CNN8
from .CASIANet import CASIANet
from .LightCNN import LightCNN9
from .LightCNN import LightCNN29
from .LightCNN import LightCNN29v2
from .MCCNN import MCCNN
from .MCCNNv2 import MCCNNv2
from .FASNet import FASNet
from .DeepMSPAD import DeepMSPAD
from .DeepPixBiS import DeepPixBiS
from .MCDeepPixBiS import MCDeepPixBiS

from .DCGAN import DCGAN_generator
from .DCGAN import DCGAN_discriminator

from .ConditionalGAN import ConditionalGAN_generator
from .ConditionalGAN import ConditionalGAN_discriminator

from .ConvAutoencoder import ConvAutoencoder

from .utils import weights_init

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]

