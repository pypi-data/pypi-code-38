# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" EDTCN module within the ketos library

    This module provides utilities to work with Encoder-Decoder Temporal-Convolutional Networks (EDTCN)

    Contents:
        EDTCN class:
"""
import tensorflow as tf
import numpy as np
from ketos.data_handling.data_handling import to1hot, from1hot
from ketos.neural_networks.neural_networks import DataHandler


def channel_normalization(x):
    """ Normalize by the highest activation.

        Args:
            x: tensor
                Tensor containing output values from layer in neural network

        Returns:
            out: tensor
                Values normalized by the highest activation
    """
    max_values = tf.keras.backend.max(tf.keras.backend.abs(x), 2, keepdims=True) + 1e-5
    out = x / max_values
    return out


class EDTCN(DataHandler):
    """ Create an Encoder-Decoder Temporal Convolutional Network (ED-TCN) for classification tasks.

        Implementation adapted from https://github.com/colincsl/TemporalConvolutionalNetworks

        The network architecture can only be constructed if the size of the input data is known.
        Therefore, either num_feat or train_x must be provided.
        In the latter case, the size is automatically determined from the input data.

        Args:
            num_feat: int
                Size of input data
            train_x: numpy array
                Training data
            train_y: numpy array
                Labels for training data. Can be integers or 1-hot encoded
            validation_x: numpy array
                Validation data
            validation_y: numpy array
                Labels for validation data. Can be integers or 1-hot encoded
            test_x: numpy array
                Test data
            test_y: numpy array
                Labels for test data. Can be integers or 1-hot encoded
            num_labels: int
                Number of labels
            max_len: int
                The input data will be split into chuncks of size max_len. 
                Thus, max_len effectively limits the extent of the memory of the network. 
            batch_size: int
                The number of examples in each batch
            num_epochs: int
                The number of epochs
            keep_prob: float
                Probability of keeping weights during training. Set keep_prob to 1.0 to disable drop-out (default).
            verbosity: int
                Verbosity level (0: no messages, 1: warnings only, 2: warnings and diagnostics)

        Attributes:
            model: tf.keras.models.Model
                Neural network model
            class_weights_func: tf.keras.backend.function
                Function to compute classification weights

        Example:

            >>> # initialize EDTCN for classifying feature vectors of size 64
            >>> from ketos.neural_networks.edtcn import EDTCN
            >>> tcn = EDTCN(num_feat=64)
            >>> print(tcn.num_feat)
            64
    """
    def __init__(self, num_feat=None, train_x=None, train_y=None, validation_x=None, validation_y=None,
                 test_x=None, test_y=None, num_labels=2, max_len=500, batch_size=4, 
                 num_epochs=100, keep_prob=0.7, verbosity=0):

        assert (num_feat is not None) or (train_x is not None), "num_feat or train_x must be provided"

        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.keep_prob = keep_prob
        self.verbosity = verbosity
        self.max_len = max_len

        self.model = None
        self.class_weights_func = None

        self.max_len = max_len

        super(EDTCN, self).__init__(train_x=train_x, train_y=train_y, 
                validation_x=validation_x, validation_y=validation_y,
                test_x=test_x, test_y=test_y, num_labels=num_labels)

        if num_feat is None:
            x, _ = self.get_training_data()
            x = np.squeeze(x)
            self.num_feat = x.shape[-1]
        else:
            self.num_feat = num_feat

    def set_verbosity(self, verbosity):
        """Set verbosity level.

            0: no messages
            1: warnings only
            2: warnings and diagnostics

            Args:
                verbosity: int
                    Verbosity level.        
        """
        self.verbosity = verbosity

    def create(self, n_nodes=[16, 32], conv_len=16, max_len=None):
        """Create the Neural Network structure.

            Args:
                n_nodes: tuple(int)
                    Number of output filters in each 1D convolutional layer.
                    (The number of convolutional layers is given by the length of n_nodes)
                conv_len: int
                    Length of the 1D convolution window.
                max_len: int
                    The input data will be split into chuncks of size max_len. 
                    Thus, max_len effectively limits the extent of the memory of the network. 

            Example:

                >>> # initialize EDTCN for classifying feature vectors of size 64
                >>> from ketos.neural_networks.edtcn import EDTCN
                >>> tcn = EDTCN(num_feat=64)
                >>> # create network with default architecture
                >>> tcn.create()
        """
        dropout_rate = 1.0 - self.keep_prob

        if max_len is not None:
            self.max_len = max_len

        # ensure that max_len is divisible by four (as this seems to be required by keras.layers.Input)
        if self.max_len % 4 > 0:
            self.max_len += 4 - self.max_len % 4
            if self.verbosity >= 1: 
                print(' Warning: max_len must be divisible by 4; max_len has been adjust to {0}'.format(self.max_len))

        n_feat = self.num_feat 
        n_layers = len(n_nodes)
        n_classes = self.num_labels
        
        # --- Input layer ---
        inputs = tf.keras.layers.Input(shape=(self.max_len, n_feat))
        model = inputs

        # ---- Encoder ----
        for i in range(n_layers):
            model = tf.keras.layers.Convolution1D(n_nodes[i], conv_len, padding='same')(model) # 1D convolutional layer
            model = tf.keras.layers.SpatialDropout1D(rate=dropout_rate)(model) # Spatial 1D version of Dropout
            model = tf.keras.layers.Activation('relu')(model) # apply activation
            model = tf.keras.layers.Lambda(channel_normalization, name="encoder_norm_{}".format(i))(model)
            model = tf.keras.layers.MaxPooling1D(2)(model) # max pooling

        # ---- Decoder ----
        for i in range(n_layers):
            model = tf.keras.layers.UpSampling1D(2)(model)
            model = tf.keras.layers.Convolution1D(n_nodes[-i-1], conv_len, padding='same')(model)
            model = tf.keras.layers.SpatialDropout1D(rate=dropout_rate)(model)
            model = tf.keras.layers.Activation('relu')(model)
            model = tf.keras.layers.Lambda(channel_normalization, name="decoder_norm_{}".format(i))(model)

        # Output fully connected layer
        model = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=n_classes, activation="softmax" ))(model)

        # create and compile model
        model = tf.keras.models.Model(inputs=inputs, outputs=model)
        model.compile(loss='categorical_crossentropy', optimizer="rmsprop", sample_weight_mode="temporal", metrics=['accuracy'])

        self.model = model

        # make function to retrieve classification weights
        inp = self.model.input                
        output = self.model.layers[-1].output
        self.class_weights_func = tf.keras.backend.function([inp, tf.keras.backend.learning_phase()], [output])

    def train(self, batch_size=None, num_epochs=None, equal_weighting=False):
        """ Train the neural network on the training set.

            Divide the training set in batches of size batch_size. 

            Args:
                batch_size: int
                    Batch size. Overwrites batch size specified at initialization.
                num_epochs: int
                    Number of epochs: Overwrites number of epochs specified at initialization.
                equal_weighting: bool
                    Correct for any imbalance in the occurrence of class examples in the training data, so 
                    that all classes are weighted equally in calculation of the loss function. 
                    Obs: only implemeted for binary classification! 

            Returns:
                history: 
                    Keras training history.
        """
        if batch_size is None:
            batch_size = self.batch_size
        if num_epochs is None:
            num_epochs = self.num_epochs

        x, y = self.get_training_data()
        x_val, y_val = self.get_validation_data()

        # ensure equal weighting of 0s and 1s
        if equal_weighting:

            y1 = from1hot(y)
            assert np.max(y) == 1, 'Equal weighting has only been implemented for binary classification'

            n0 = np.sum(y1==0)
            n = y1.shape[0]
            w0 = float(n - n0) / float(n)
            sample_weight = y1 * (1. - w0) - (y1 - 1) * w0
            sample_weight = self._reshape(sample_weight[:, np.newaxis])
            sample_weight = np.squeeze(sample_weight)            
        
        else:
            sample_weight = None

        if x_val is not None and y_val is not None:
            x_val = self._reshape(x_val)
            y_val = self._reshape(y_val)
            val_data = (x_val, y_val)
        else:
            val_data = None

        x = self._reshape(x)
        y = self._reshape(y)

        history = self.model.fit(x=x, y=y, batch_size=batch_size, epochs=num_epochs,\
                    verbose=self.verbosity, validation_data=val_data, sample_weight=sample_weight)   
        return history     

    def get_predictions(self, x):
        """ Predict labels by running the model on x

            Args:
                x: tensor
                    Tensor containing the input data.
                
            Returns:
                results: vector
                    A vector containing the predicted labels.                
        """
        x = np.array(x)

        if np.ndim(x) == 1:
            x = x[np.newaxis, :]

        orig_len = x.shape[0]

        x = self._reshape(x)
        results = self.model.predict(x=x)
        results = np.reshape(results, newshape=(results.shape[0]*results.shape[1], results.shape[2]))

        results = from1hot(results)
        results = results[:orig_len]

        if results.shape[0] == 1:
            results = results[0]

        return results

    def get_class_weights(self, x):
        """ Compute classification weights by running the model on x.

            Args:
                x: tensor
                    Tensor containing the input data.
                
            Returns:
                results: vector
                    A vector containing the classification weights. 
        """
        x = np.array(x)

        if np.ndim(x) == 1:
            x = x[np.newaxis, :]

        orig_len = x.shape[0]

        x = self._reshape(x)        
        w = np.array(self.class_weights_func([x, False]))
        w = np.squeeze(w)
        if np.ndim(w) == 2:
            w = w[np.newaxis,:,:]
            
        w = np.reshape(w, newshape=(w.shape[0]*w.shape[1], w.shape[2]))

        w = w[:orig_len]
        if w.shape[0] == 1:
            w = w[0]

        return w

    def _reshape(self, a):
        """ Split the data into chunks with size max_len.
            
            Args:
                a: numpy array
                    Array containing the data to be split.
        """
        if np.ndim(a) > 2:
            a = np.squeeze(a)

        n = self.max_len
        orig_len = a.shape[0]
        nsegs = int(np.ceil(orig_len / n))
        new_len = nsegs * n

        pad_shape = np.array([new_len - orig_len], dtype=np.int32)
        pad_shape = np.append(pad_shape, a.shape[1:])
        a = np.append(a, np.zeros(shape=pad_shape), axis=0)

        new_shape = np.array([nsegs, n], dtype=np.int32)
        new_shape = np.append(new_shape, a.shape[1:])
        a = np.reshape(a=a[:new_len], newshape=new_shape)

        return a

    def save(self, destination):
        """ Save the model to destination

            Args:
                destination: str
                    Path to the file in which the model will be saved. 

            Returns:
                None.
        
        """
        tf.keras.models.save_model(model=self.model, filepath=destination)

    # TODO: The current implementation of the load() method does not work.
    #       It gives the error message "in channel_normalization max_values 
    #       = tf.keras.backend.max(tf.keras.backend.abs(x), 2, keepdims=True) 
    #       + 1e-5 NameError: name 'tf' is not defined"

    def load(self, path):
        """Load the Neural Network structure and weights from a saved model.

            See the save() method. 

            Args:
                path: str
                    Path to the saved model.
        """
        self.model = tf.keras.models.load_model(filepath=path)

    def save_weights(self, path):
        """ Save the model weights to destination

            Args:
                destination: str
                    Path to the file in which the weights will be saved. 

            Returns:
                None.
        """
        self.model.save_weights(filepath=path)        

    def load_weights(self, path):
        """ Load the model weights

            Args:
                destination: str
                    Path to the file in which the weights are stored.

            Returns:
                None.
        """
        self.model.load_weights(filepath=path)        