import torch
import torch.nn
import torch.nn.functional as F
import torchvision.models as models


class MLP(torch.nn.Module):
    def __init__(self, x_dim, y_dim, dropout=None):
        super().__init__()
        self.apply_dropout = dropout is not None
        self.linear_1 = torch.nn.Linear(x_dim, 512)
        self.dropout_1 = torch.nn.Dropout(dropout if dropout is not None else 0)
        self.linear_2 = torch.nn.Linear(512, 512)
        self.dropout_2 = torch.nn.Dropout(dropout if dropout is not None else 0)
        self.linear_3 = torch.nn.Linear(512, y_dim)

    def forward(self, x):
        h = F.relu(self.linear_1(x))
        if self.apply_dropout:
            h = self.dropout_1(h)
        h = F.relu(self.linear_2(h))
        if self.apply_dropout:
            h = self.dropout_2(h)
        return F.softmax(self.linear_3(h), dim=1)


class MLPSmall(torch.nn.Module):
    def __init__(self, x_dim, y_dim, dropout=None):
        super().__init__()
        self.apply_dropout = dropout is not None
        self.linear_1 = torch.nn.Linear(x_dim, 32)
        self.dropout_1 = torch.nn.Dropout(dropout if dropout is not None else 0)
        self.linear_2 = torch.nn.Linear(32, y_dim)

    def forward(self, x):
        h = F.relu(self.linear_1(x))
        if self.apply_dropout:
            h = self.dropout_1(h)
        return F.softmax(self.linear_2(h), dim=1)
