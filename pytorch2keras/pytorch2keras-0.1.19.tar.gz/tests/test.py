from pytorch2keras.converter import pytorch_to_keras
from torch import nn
from torch.nn import functional as F
import torch

import torch
import torch.nn as nn
import torch.nn.functional as F


class Bottleneck(nn.Module):
    def __init__(self, inp_c, out_c, kernel_size, stride, t=1):
        assert stride in [1, 2], 'stride must be either 1 or 2'
        super().__init__()
        self.residual = stride == 1 and inp_c == out_c
        # pad = kernel_size // 2
        # self.reflection_pad = nn.ReflectionPad2d(pad)
        self.conv1 = nn.Conv2d(inp_c, t*inp_c, 1, 1, bias=False)
        self.in1 = nn.InstanceNorm2d(t*inp_c, affine=True)
        self.conv2 = nn.Conv2d(t*inp_c, t*inp_c, kernel_size, stride,
                               groups=t*inp_c, bias=False, padding=kernel_size//2)
        self.in2 = nn.InstanceNorm2d(t*inp_c, affine=True)
        self.conv3 = nn.Conv2d(t*inp_c, out_c, 1, 1, bias=False)
        self.in3 = nn.InstanceNorm2d(out_c, affine=True)

    def forward(self, x):
        out = F.relu6(self.in1(self.conv1(x)))
        # out = self.reflection_pad(out)
        out = F.relu6(self.in2(self.conv2(out)))
        out = self.in3(self.conv3(out))
        if self.residual:
            out = x + out
        return out


class UpsampleConv(nn.Module):
    def __init__(self, inp_c, out_c, kernel_size, stride, upsample=2):
        super().__init__()
        if upsample:
            self.upsample=upsample
            # self.upsample = nn.Upsample(mode='bilinear', scale_factor=upsample, align_corners=False)
            self.upsample = nn.Upsample(mode='nearest', scale_factor=2)
        else:
            self.upsample = None
        self.conv1 = Bottleneck(inp_c, out_c, kernel_size, stride)

    def forward(self, x):
        x_in = x
        if self.upsample is not None:
            x_in = self.upsample(x_in)
        out = F.relu(self.conv1(x_in))
        return out


class TransformerMobileNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Conv Layers
        # self.reflection_pad = nn.ReflectionPad2d(9//2)
        self.conv1 = nn.Conv2d(3, 32, kernel_size=9, stride=1, bias=False, padding=9//2)
        self.in1 = nn.InstanceNorm2d(32, affine=True)
        self.conv2 = Bottleneck(32, 64, kernel_size=3, stride=2)
        self.conv3 = Bottleneck(64, 128, kernel_size=3, stride=2)
        # Residual Layers
        self.res1 = Bottleneck(128, 128,  3, 1)
        self.res2 = Bottleneck(128, 128,  3, 1)
        self.res3 = Bottleneck(128, 128,  3, 1)
        self.res4 = Bottleneck(128, 128,  3, 1)
        self.res5 = Bottleneck(128, 128,  3, 1)
        # Upsampling Layers
        self.upconv1 = UpsampleConv(128, 64, kernel_size=3, stride=1)
        self.upconv2 = UpsampleConv(64, 32, kernel_size=3, stride=1)
        self.conv4 = nn.Conv2d(32, 3, kernel_size=9, stride=1, bias=False, padding=9//2)

    def forward(self, x):
        # out = self.reflection_pad(x)
        out = F.relu(self.in1(self.conv1(x)))
        out = self.conv2(out)
        # out = self.conv3(out)
        # out = self.res1(out)
        # out = self.res2(out)
        # out = self.res3(out)
        # out = self.res4(out)
        # out = self.res5(out)
        # out = self.upconv1(out)
        # out = self.upconv2(out)
        # out = self.conv4(out)
        return out

# if __name__ == "__main__":
#     from torchsummary import summary
#     model = TransformerMobileNet()
#     model.to('cuda')
#     summary(model, (3, 256, 256))
#     model.load_state_dict(torch.load('saved_model/release.pth'))
#     torch.onnx.export(model, torch.randn(1, 3, 256, 256).cuda(), 'models/style1.onnx')
import numpy as np
with torch.no_grad():
    test_net = TransformerMobileNet()
    test_net.eval()
    dummy_input = torch.ones([1, 3, 256, 256])
    dummy_output = test_net(dummy_input)

    print(test_net(dummy_input))
    t_model = pytorch_to_keras(test_net, dummy_input, [(3, 256, 256)], change_ordering=True, verbose=True)
    t_model.summary()
    t_model.save('t_model.h5')

    k_pred = t_model.predict(np.ones((1, 256, 256, 3)))
    print(k_pred - dummy_output.permute(0, 2, 3, 1).numpy())