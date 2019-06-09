__version__ = '0.3.0'
git_version = 'eb7a0f40ca7a7e269e893c1a8ab5845085c8b219'
from torchvision import _C
if hasattr(_C, 'CUDA_VERSION'):
    cuda = _C.CUDA_VERSION
