import random

import torch
import numpy as np
from torch import nn
from visdom import Visdom

class AverageMeter(object):
    """Keeps track of most recent, average, sum, and count of a metric.

    Example
    -------
    losses = AverageMeter()
    losses.update(1, 5)
    print(losses.avg)
    """

    def __init__(self):
        self.reset()

    def reset(self):
        # Reset all value to 0.
        self.value = 0
        self.avg   = 0
        self.sum   = 0
        self.count = 0

    def update(self, value, n=1):
        """Update value, average, sum, and count.

        Parameters
        ----------
        n : int, optional (default = 5)
        value : double

        """
        self.value = value
        self.sum   += value * n
        self.count += n
        self.avg   = self.sum / self.count

class VisdomLinePlotter(object):
    """Plots lines in Visdom.

    Parameter
    ----------
    env_name: str, optional (default = 'main')
        Environment name of Visdom, you should not change it if don't know what's going on.

    Example
    -------
    import time

    plotter = VisdomLinePlotter()
    for x, y in zip(range(10), range(10)):
        plotter.plot("var_name", "split_name", "title_name", x, y)
        time.sleep(2)
    """
    def __init__(self, env_name='main'):
        self.viz = Visdom()
        self.env = env_name
        self.plots = {}

    def plot(self, var_name, split_name, title_name, x, y):
        if var_name not in self.plots:
            self.plots[var_name] = self.viz.line(X   = np.array([x,x]),
                                                 Y   = np.array([y,y]),
                                                 env = self.env,
                                                 opts= dict(legend = [split_name],
                                                           title   = title_name,
                                                           xlabel  = 'Epochs',
                                                           ylabel  = var_name))

        else:
            self.viz.line(X      = np.array([x]),
                          Y      = np.array([y]),
                          env    = self.env,
                          win    = self.plots[var_name],
                          name   = split_name,
                          update = 'append')

def pytorch_reproducer(device="cpu", seed=2019):
    """Reproducer for pytorch experiment.

    Parameters
    ----------
    seed: int, optional (default = 2019)
    	Radnom seed.
    device: str, optinal (default = "cpu")
    	Device type.

    Example
    -------
    pytorch_reproducer(seed=2019, device=DEVICE).
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if device == 'cuda':
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = True

def get_device():
    """Return device type.

    Return
    ------
    DEVICE: torch.device

    Example
    -------
    DEVICE = get_device()
    """
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return DEVICE

def clip_gradient(optimizer, grad_clip):
    """Clip gradients computed during backpropagation to prevent gradient explosion.

     Parameters
     ----------
     optimizer: pytorch optimizer
     	Optimized with the gradients to be clipped.
     grad_clip: double
     	Gradient clip value.

     Example
     -------
     from torch.optim import Adam
     from torchvision import models

     model = models.AlexNet()
     optimizer = Adam(model.parameters())
     clip_gradient(optimizer, 5)
     """
    for group in optimizer.param_groups:
        for param in group['params']:
            if param.grad is not None:
                param.grad.data.clamp_(-grad_clip, grad_clip)

def adjust_learning_rate(optimizer, scale_factor):
    """Shrinks learning rate by a specified factor.

    Parameters
    ----------
    optimizer: pytorch optimizer
    scale_factor: factor to scale by
    """

    print("\nDECAYING learning rate.")
    for param_group in optimizer.param_groups:
        param_group['lr'] = param_group['lr'] * scale_factor
    print("The new learning rate is %f\n" % (optimizer.param_groups[0]['lr'],))

def get_learning_rate(optimizer):
    """Get learning rate.

    Parameters
    ----------
    optimizer: pytorch optimizer
    """
    lr=[]
    for param_group in optimizer.param_groups:
       lr +=[ param_group['lr'] ]

    assert(len(lr)==1) #we support only one param_group
    lr = lr[0]

    return lr

def init_conv2d(m):
    """Init parameters of convolution layer(初始化卷积层参数)

       Parameters
       ----------
       m: pytorch model

       Example
       -------
       class model(nn.Module):

           def __init__(self):
               super().__init__()

               # 初始化卷积层权重
               init_conv2d(self)
    """
    # 遍历网络子节点
    for c in m.modules():
        # 初始化卷积层
        if isinstance(c, nn.Conv2d):
            nn.init.xavier_uniform_(c.weight)
            nn.init.kaiming_normal_(c.weight, mode='fan_out', nonlinearity='relu')
            if c.bias is not None:
                nn.init.constant_(c.bias, 0.)
        # 初始BatchNorm层
        elif isinstance(c, nn.BatchNorm2d):
            nn.init.constant_(c.weight, 1.)
            nn.init.constant_(c.bias, 0.)
        # 初始线性层
        elif isinstance(c, nn.Linear):
            nn.init.normal_(c.weight, 0., 0.01)
            nn.init.constant_(c.bias, 0.)

def decimate(tensor, dims):
    """将tensor的维度变为dims
       Parameters
       ----------
       tensor: pytorch tensor
       dims: list

       Example
       -------
       x = torch.rand(4096, 512, 7, 7)
       decimate(x, [1024, None, 3, 3])
    """
    assert tensor.dim() == len(dims)

    for i in range(len(dims)):
        if dims[i] is not None:
            tensor = tensor.index_select(dim=i, index=torch.linspace(0, tensor.size()[i]-1, dims[i]).long())

    return tensor
