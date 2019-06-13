from pytorch2keras.converter import pytorch_to_keras
from torch import nn
from torch.nn import functional as F
import torch

class PCN2(nn.Module):

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 20, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(20, 40, kernel_size=3, stride=1)
        self.conv3 = nn.Conv2d(40, 70, kernel_size=2, stride=1)
        self.fc = nn.Linear(1750, 140)
        self.rotate = nn.Linear(140, 3)
        self.cls_prob = nn.Linear(140, 2)
        self.bbox = nn.Linear(140, 3)
        self.mp = nn.MaxPool2d(kernel_size=3, stride=2)

    def forward(self, x):
        batch_size = x.size(0)
        x = self.conv1(x)
        x = F.pad(x, (0, 1, 0, 1))
        x = F.relu(self.mp(x), inplace=True)
        x = self.conv2(x)
        x = F.pad(x, (0, 1, 0, 1))
        x = F.relu(self.mp(x), inplace=True)
        x = F.relu(self.conv3(x), inplace=True)
        x = x.view(batch_size, -1)
        x = F.relu(self.fc(x), inplace=True)
        cls_prob = F.softmax(self.cls_prob(x), dim=1)
        rotate = F.softmax(self.rotate(x), dim=1)
        bbox = self.bbox(x)
        return cls_prob, rotate, bbox

test_net = PCN2()
dummy_input = torch.ones([1, 3, 32, 32])
t_model = pytorch_to_keras(test_net, dummy_input, [(3, 32, 32)], verbose=True)
t_model.save('t_model.h5')