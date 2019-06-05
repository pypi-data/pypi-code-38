from keras.layers import Conv2D, Activation, Dense, Flatten, BatchNormalization, MaxPooling2D, AveragePooling2D, Dropout
from keras.engine import InputLayer
from keras.optimizers import Adadelta

from boarml.builders.base_builder import BaseBuilder
from keras import Sequential

from boarml.cnn import Layers
from boarml.cnn import Model


class KerasBuilder(BaseBuilder):

    def build(self, layers):
        model = Sequential()

        for layer in layers:
            model.add(self.create_layer(layer))

        opt = Adadelta()
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

        return Model(model, 'keras')

    def create_layer(self, layer):
        layer_type = layer.type

        if layer_type == Layers.CONV:
            return Conv2D(filters=layer.filters, kernel_size=layer.kernel_size, strides=layer.strides, padding='same')
        elif layer_type == Layers.ACTIVATION:
            return Activation(layer.func)
        elif layer_type == Layers.INPUT:
            return InputLayer(input_shape=layer.shape)
        elif layer_type == Layers.DENSE:
            return Dense(units=layer.nodes)
        elif layer_type == Layers.FLATTEN:
            return Flatten()
        elif layer_type == Layers.DROPOUT:
            return Dropout(rate=layer.rate)
        elif layer_type == Layers.POOLING:
            if layer.operation == 'max':
                return MaxPooling2D(pool_size=layer.pool_size, strides=layer.strides, padding='same')
            elif layer.operation == 'average':
                return AveragePooling2D(pool_size=layer.pool_size, strides=layer.strides, padding='same')
        elif layer_type == Layers.BATCH_NORM:
            return BatchNormalization(momentum=layer.momentum)
