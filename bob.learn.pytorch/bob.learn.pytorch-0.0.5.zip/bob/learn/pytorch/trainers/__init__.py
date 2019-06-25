from .CNNTrainer import CNNTrainer
from .MCCNNTrainer import MCCNNTrainer
from .DCGANTrainer import DCGANTrainer
from .ConditionalGANTrainer import ConditionalGANTrainer
from .FASNetTrainer import FASNetTrainer
from .GenericTrainer import GenericTrainer

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]

