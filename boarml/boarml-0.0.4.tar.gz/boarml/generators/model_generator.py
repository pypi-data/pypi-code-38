import copy, os

from boarml.architectures.cnn_architecture import CnnBaseArchitecture
from boarml.cnn.layers import Layers, ConvLayer, DropoutLayer, BatchNormalizationLayer, PoolingLayer
from boarml.cnn.unit import Unit
from random import Random
from boarml.builders.keras_builder import KerasBuilder


class ModelGenerator:

    def __init__(self, architecture, builder, removal_rate=0.5, duplication_rate=0.5, amendment_rate=0.5, seed=None):
        self.architecture = architecture
        self.builder = builder
        self.removal_rate = removal_rate
        self.duplication_rate = duplication_rate
        self.amendment_rate = amendment_rate
        self.rnd = Random(seed)

        self.mutation_history = list()

    def create_base_model(self):
        return self.create_model(self.architecture)

    def create_mutated_model(self):

        generate_new = True

        while generate_new:
            generate_new = False

            main_units = self.mutate_main_units(self.architecture)
            mutated_architecture = CnnBaseArchitecture(self.architecture.input_shape, self.architecture.output_shape)
            mutated_architecture.main_arch = main_units

            # If is in the history generate new
            for m in self.mutation_history:
                if str(m) == str(mutated_architecture):
                    generate_new = True

            # If it is invalid generate new
            if not self.is_valid_architecture(mutated_architecture):
                generate_new = True

        self.mutation_history.append(mutated_architecture)
        return self.create_model(mutated_architecture)

    def create_model(self, architecture):

        layers = list()

        for layer in architecture.input_arch:
            layers.append(layer)

        for unit in architecture.main_arch:
            for layer in unit.layers:
                layers.append(layer)

        for layer in architecture.output_arch:
            layers.append(layer)

        if self.builder == 'keras':
            model = KerasBuilder().build(layers)
            return model
        else:
            raise Exception('Unknown builder!')

    def mutate_main_units(self, architecture):

        units = list()

        for unit in architecture.main_arch:

            # Duplicate
            if self.duplication_rate > self.rnd.random():
                units.append(copy.deepcopy(unit))

            # Remove
            if self.removal_rate > self.rnd.random():
                pass
            else:
                # Amend
                if self.amendment_rate > self.rnd.random():
                    units.append(self.unit_mutation(unit))
                else:
                    units.append(unit)

        return units

    def unit_mutation(self, unit):
        mutated_unit = Unit()

        for layer in unit.layers:

            # Mutate Convolutional Layer
            if layer.type == Layers.CONV:
                mutated_layer = self.mutate_conv(layer)
            # Mutate Batch Normalisation Layer
            elif layer.type == Layers.BATCH_NORM:
                mutated_layer = self.mutate_batch_norm(layer)
            # Mutate Max Pooling Layer
            elif layer.type == Layers.POOLING:
                mutated_layer = self.mutate_pooling(layer)
            # Mutate Dropout Layer
            elif layer.type == Layers.DROPOUT:
                mutated_layer = self.mutate_dropout(layer)
            # Just add the layer
            else:
                mutated_layer = layer

            if mutated_layer is not None:
                mutated_unit.add_layer(mutated_layer)

        return mutated_unit

    def mutate_conv(self, layer):

        mutated = None

        choices = ['filter', 'kernel', 'stride']

        selected = self.rnd.choice(choices)

        if selected == 'filter':
            filters_choices = [64, 128, 256, 320, 512, 700]
            filter_selected = self.rnd.choice(filters_choices)

            mutated = ConvLayer(filters=filter_selected, kernel_size=layer.kernel_size, strides=layer.strides)

        if selected == 'kernel':
            kernel_choice = [(1, 1), (3, 3), (5, 5), (7, 7)]
            kernel_selected = self.rnd.choice(kernel_choice)

            mutated = ConvLayer(filters=layer.filters, kernel_size=kernel_selected, strides=layer.strides)

        if selected == 'stride':
            stride_choice = [(1, 1), (2, 2), (3, 3)]
            stride_selected = self.rnd.choice(stride_choice)

            mutated = ConvLayer(filters=layer.filters, kernel_size=layer.kernel_size, strides=stride_selected)

        return mutated

    def mutate_dropout(self, layer):

        mutated = None

        choices = ['rate', 'remove']

        selected = self.rnd.choice(choices)

        if selected == 'rate':
            rate_choices = [0.1, 0.2, 0.3, 0.4, 0.5]
            rate_selected = self.rnd.choice(rate_choices)

            mutated = DropoutLayer(rate=rate_selected)

        if selected == 'remove':
            pass

        return mutated

    def mutate_batch_norm(self, layer):

        mutated = None

        choices = ['momentum', 'remove']

        selected = self.rnd.choice(choices)

        if selected == 'momentum':
            momentum_choices = [0.99, 0.95, 0.90, 0.85]
            momentum_selected = self.rnd.choice(momentum_choices)

            mutated = BatchNormalizationLayer(momentum=momentum_selected)

        if selected == 'remove':
            pass

        return mutated

    def mutate_pooling(self, layer):

        mutated = None

        choices = ['operation', 'pool_size', 'remove']

        selected = self.rnd.choice(choices)

        if selected == 'operation':
            operation_choices = ['max', 'average']
            operation_selected = self.rnd.choice(operation_choices)

            mutated = PoolingLayer(operation=operation_selected, pool_size=layer.pool_size, strides=layer.strides)

        if selected == 'pool_size':
            pool_size_choices = [(2, 2), (3, 3)]
            pool_size_selected = self.rnd.choice(pool_size_choices)

            mutated = PoolingLayer(operation=layer.operation, pool_size=pool_size_selected, strides=layer.strides)

        if selected == 'remove':
            pass

        return mutated

    def get_last_mutation(self):
        if len(self.mutation_history) > 0:
            return self.mutation_history[-1]
        else:
            return self.architecture

    def populate_history(self, path, name, count):

        for i in range(0, count):
            full_name = name + str(i) + '.txt'

            full_path = os.path.join(path, full_name)
            arch = CnnBaseArchitecture()
            arch.build_from_file(full_path)

            self.mutation_history.append(arch)

    def is_valid_architecture(self, architecture):
        valid = True

        if len(architecture.main_arch) == 0:
            valid = False

        return valid
