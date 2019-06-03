from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras import backend as K


class LeNet:
    @staticmethod
    def build(width, height, depth, classes, last_active="softmax"):
        # Initialize the model
        model = Sequential()
        input_shape = (height, width, depth)

        # If we are using 'channels-first', update the input shape
        if K.image_data_format() == 'channels_first':
            input_shape = (depth, height, width)

        # First set of CONV => RELU => POOL layers
        model.add(Conv2D(20, (5, 5), padding='same', input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        # Second set of CONV => RELU => POOL layers
        model.add(Conv2D(50, (5, 5), padding='same'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        # First (and only) set of FC => RELU layers
        model.add(Flatten())
        model.add(Dense(500))
        model.add(Activation('relu'))

        model.add(Dense(classes))
        model.add(Activation(last_active))
            
        # return the constructed network architecture
        return model
