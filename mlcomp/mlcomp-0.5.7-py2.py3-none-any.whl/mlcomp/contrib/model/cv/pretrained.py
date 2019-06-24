import torch.nn as nn
import pretrainedmodels


class Pretrained(nn.Module):
    def __init__(self, variant, n_classes):
        super().__init__()
        res = pretrainedmodels.__dict__[variant]()

        self.l1 = nn.Sequential(*list(res.children())[:-1]).to('cuda:0')
        self.last = nn.Linear(res.last_linear.in_features, n_classes)

    def forward(self, x):
        x = self.l1(x)
        x = x.view(x.size()[0], -1)
        x = self.last(x)
        return x


__all__ = ['Pretrained']
