import torch.nn as nn
import torch.utils.model_zoo as model_zoo


__all__ = ['AlexNet']

model_urls = {
    'alexnet': 'https://download.pytorch.org/models/alexnet-owt-4df8aa71.pth',
}

class _AlexNet(nn.Module):

    def __init__(self, num_classes=1000):
        super(_AlexNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), 256 * 6 * 6)
        x = self.classifier(x)
        return x

class AlexNet(_AlexNet):
    def __init__(self, layer, input_shape):
        model_param = layer['model_param']
        self.num_classes = int(model_param.get('num_classes', 1000))
        pretrained = (model_param.get('pretrained', 'false') == 'true')
        super(AlexNet, self).__init__(self.num_classes)
        if pretrained:
            self.load_state_dict(model_zoo.load_url(model_urls['alexnet']))

    def forward_shape(self, input_shape):
        return [input_shape[0], self.num_classes]



