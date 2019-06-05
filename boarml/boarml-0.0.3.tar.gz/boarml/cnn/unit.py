class Unit:
    UNIT_SYMBOL = '-Unit-'

    def __init__(self):
        self.layers = list()

    def add_layer(self, layer):
        self.layers.append(layer)

    @property
    def size(self):
        return len(self.layers)

    def __str__(self):
        layer_count = len(self.layers)
        text = f'{Unit.UNIT_SYMBOL}({layer_count})'
        newline = '\n'

        for layer in self.layers:
            text = text + newline + str(layer)

        return text
