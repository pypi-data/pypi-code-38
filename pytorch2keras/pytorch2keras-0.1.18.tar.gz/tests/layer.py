import numpy as np
import torch
from torch.autograd import Variable
from pytorch2keras.converter import pytorch_to_keras
import torchvision

import torch.nn as nn

class LayerTest(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 10)
        self.fc2 = nn.Linear(5, 10)

    def forward(self, x, y):
        x = self.fc1(x)
        y = self.fc2(y)
        return x + y

model = LayerTest().eval()
input_x = torch.FloatTensor(np.random.uniform(0, 1, (1, 10)))
input_y = torch.FloatTensor(np.random.uniform(0, 1, (1, 5)))
output = model(input_x, input_y)
k_model = pytorch_to_keras(model, [input_x, input_y], [(10,), (5,)], verbose=True)

print(output)
print(k_model.predict([input_x.numpy(), input_y.numpy()]))
