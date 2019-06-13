import torch
import torch.nn as nn
import numpy as np
from torch.autograd import Variable

class PytorchModel(nn.Module):
    def __init__(self):
        super(PytorchModel, self).__init__()
        self.bn = nn.BatchNorm2d(1, momentum=0.5)

    def forward(self, x):
        x = self.bn(x)
        return x

pytorch_model = PytorchModel()
pytorch_model.eval()

x_data = np.random.uniform(0, 1, size=(1, 1, 224, 224))
x = Variable(torch.Tensor(x_data))

torch_out = torch.onnx._export(pytorch_model, x, "model.onnx", export_params=True)