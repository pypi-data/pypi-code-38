from catalyst.dl import registry
from mlcomp.contrib.model import Pretrained
from mlcomp.contrib.criterion import RingLoss
from mlcomp.contrib.catalyst.callbacks.inference import InferBestCallback

def register():
    registry.Model(Pretrained)

    registry.Criterion(RingLoss)

    registry.Callback(InferBestCallback)
