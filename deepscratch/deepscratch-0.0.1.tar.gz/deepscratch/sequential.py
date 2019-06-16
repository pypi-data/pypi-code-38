

class Sequential:
    def __init__(self, layers=None, name='Sequential'):
        self.name = name
        self.layers = layers

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def backward(self, grad):
        for layer in reversed(self.layers):
            grad = layer.backward(grad)

    def __repr__(self):
        result = ''
        result += f'\033[01m{self.name}\033[00m ( \n'
        
        for layer in self.layers:
            result += f'\t{layer.__repr__()} \n'.expandtabs(4)

        result += ')'
        return result
