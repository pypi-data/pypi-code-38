from boarml.cnn import *
from enum import IntEnum


class ArchSection(IntEnum):
    INPUT = 1
    MAIN = 2
    OUTPUT = 3
    START = 4
    END = 5
    UNIT = 6


MAIN_ARCH_SYMBOLS = {ArchSection.START: '<<<<<START>>>>>', ArchSection.INPUT: '---Input---', ArchSection.MAIN: '---Main---',
                     ArchSection.UNIT: Unit.UNIT_SYMBOL,
                     ArchSection.OUTPUT: '---Output---', ArchSection.END: '<<<<<END>>>>>'}


class CnnBaseArchitecture:

    def __init__(self, input_shape=0, output_nodes=0):
        self.layers = dict()

        self.input_shape = input_shape
        self.output_shape = output_nodes

        self.__add_input_layers(input_shape)
        self.__add_output_layers(output_nodes)

        self.layers[ArchSection.MAIN] = list({Unit()})
        self.main_units_count = 0

    def __add_input_layers(self, input_shape):
        input_layers = list()
        input_layers.append(InputLayer(shape=input_shape))
        self.layers[ArchSection.INPUT] = input_layers

    def __add_output_layers(self, output_shape):
        output_layers = list()
        output_layers.append(FlattenLayer())
        output_layers.append(DenseLayer(nodes=output_shape))
        output_layers.append(ActivationLayer('softmax'))

        self.layers[ArchSection.OUTPUT] = output_layers

    def new_unit(self):
        if self.layers[ArchSection.MAIN][self.main_units_count].size > 0:
            self.layers[ArchSection.MAIN].append(Unit())
            self.main_units_count = self.main_units_count + 1

    def add_to_unit(self, layer):
        self.layers[ArchSection.MAIN][self.main_units_count].add_layer(layer)

    @property
    def input_arch(self):
        return self.layers[ArchSection.INPUT]

    @input_arch.setter
    def input_arch(self, input_layers):
        self.layers[ArchSection.INPUT] = input_layers

    @property
    def main_arch(self):
        return self.layers[ArchSection.MAIN]

    @main_arch.setter
    def main_arch(self, units):
        self.layers[ArchSection.MAIN] = units

    @property
    def output_arch(self):
        return self.layers[ArchSection.OUTPUT]

    @output_arch.setter
    def output_arch(self, output_layers):
        self.layers[ArchSection.OUTPUT] = output_layers

    def __str__(self):
        text = ''
        newline = '\n'

        text = f'{text}{MAIN_ARCH_SYMBOLS[ArchSection.START]}'

        # Convert Input to string
        input_count = len(self.input_arch)
        text = f'{text}{newline}{MAIN_ARCH_SYMBOLS[ArchSection.INPUT]}({input_count})'
        for layer in self.input_arch:
            text = f'{text}{newline}{layer}'

        # Convert Main to string
        main_count = len(self.main_arch)
        text = f'{text}{newline}{MAIN_ARCH_SYMBOLS[ArchSection.MAIN]}({main_count})'
        for main_unit in self.main_arch:
            text = f'{text}{newline}{main_unit}'

        # Convert Output to string
        output_count = len(self.output_arch)
        text = f'{text}{newline}{MAIN_ARCH_SYMBOLS[ArchSection.OUTPUT]}({output_count})'
        for layer in self.output_arch:
            text = f'{text}{newline}{layer}'

        text = f'{text}{newline}{MAIN_ARCH_SYMBOLS[ArchSection.END]}'

        return text

    def build_from_file(self, path):
        with open(path, 'r+') as file:
            text = file.read().splitlines()
            return self.build_from_text(text)

    def build_from_text(self, text):

        if text[0] != MAIN_ARCH_SYMBOLS[ArchSection.START]:
            raise Exception(
                f'The start of the architecture is not well defined!\nYou must use {MAIN_ARCH_SYMBOLS[ArchSection.START]} to indicate the start!')

        if text[-1] != MAIN_ARCH_SYMBOLS[ArchSection.END]:
            raise Exception(
                f'The end of the architecture is not well defined!\nYou must use {MAIN_ARCH_SYMBOLS[ArchSection.END]} to indicate the end!')

        line_index = 1

        if text[line_index].startswith(MAIN_ARCH_SYMBOLS[ArchSection.INPUT]):
            line_index = self.build_input_from_text(line_index, text)

        if text[line_index].startswith(MAIN_ARCH_SYMBOLS[ArchSection.MAIN]):
            line_index = self.build_main_from_text(line_index, text)

        if text[line_index].startswith(MAIN_ARCH_SYMBOLS[ArchSection.OUTPUT]):
            self.build_output_from_text(line_index, text)

        return self

    def build_output_from_text(self, line_index, text):
        layers_count = self.extract_number(text[line_index])
        otput_layers = list()

        for layer_index in range(1, layers_count + 1):
            layer = LayerBuilder.build_from_text(text[line_index + layer_index])

            if layer.type == Layers.DENSE:
                self.output_shape = layer.nodes

            otput_layers.append(layer)

        self.output_arch = otput_layers

    def build_main_from_text(self, line_index, text):
        unit_count = self.extract_number(text[line_index])
        main_units = list()
        line_index = line_index + 1

        for unit_index in range(1, unit_count + 1):

            layers_count = self.extract_number(text[line_index])
            unit = Unit()

            for layer_index in range(1, layers_count + 1):
                unit.add_layer(LayerBuilder.build_from_text(text[line_index + layer_index]))

            main_units.append(unit)

            line_index = line_index + layers_count + 1
        self.main_arch = main_units
        return line_index

    def build_input_from_text(self, line_index, text):
        layers_count = self.extract_number(text[line_index])
        input_layers = list()

        for layer_index in range(1, layers_count + 1):

            layer = LayerBuilder.build_from_text(text[line_index + layer_index])

            if layer.type == Layers.INPUT:
                self.input_shape = layer.shape

            input_layers.append(layer)

        self.input_arch = input_layers
        line_index = line_index + layers_count + 1

        return line_index

    def extract_number(self, line):

        return int(''.join(filter(str.isdigit, line)))
