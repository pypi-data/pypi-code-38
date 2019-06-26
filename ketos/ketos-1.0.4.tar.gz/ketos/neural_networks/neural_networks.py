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

""" Neural networks module within the ketos library

    This module provides utilities to work with Neural Networks.

    Contents:
        DataHandler class:
        DataUse class:
"""
import numpy as np
from enum import Enum
from ketos.data_handling.data_handling import check_data_sanity, to1hot


def class_confidences(class_weights):
    """ Compute the classification confidence from classification weights.

        Confidence is computed as the difference between the largest class weight 
        and the second largest class weight.

        Args:
            class_weights: numpy array
                Classification weights

        Returns:
            conf: numpy array
                Confidence level

        Example:

            >>> from ketos.neural_networks.neural_networks import class_confidences
            >>> weights = [0.2, 0.55, 0.25]
            >>> conf = class_confidences(weights)
            >>> print('{:.2f}'.format(conf))
            0.30
    """
    w = class_weights

    if type(w) is not np.ndarray:
        w = np.array(class_weights)
        w = np.squeeze(w)

    if np.ndim(w) == 1:
        w = w[np.newaxis, :]

    idx = np.argsort(w, axis=1)
    w0 = np.choose(idx[:,-1], w.T) # max weights
    w1 = np.choose(idx[:,-2], w.T) # second largest weights
    conf = w0 - w1 # classification confidence

    if len(conf) == 1:
        conf = conf[0]

    return conf

def predictions(class_weights):
    """ Compute predicted labels from classification weights.

        Args:
            class_weights: numpy array
                Classification weights

        Returns:
            p: numpy array
                Predicted labels

        Example:

            >>> from ketos.neural_networks.neural_networks import predictions
            >>> weights = [0.2, 0.55, 0.25]
            >>> pred = predictions(weights)
            >>> print(pred)
            1
    """
    w = class_weights

    if type(w) is not np.ndarray:
        w = np.array(class_weights)
        w = np.squeeze(w)

    if np.ndim(w) == 1:
        w = w[np.newaxis, :]
    
    p = np.argmax(w, axis=1)

    if len(p) == 1:
        p = p[0]

    return p     
    
class DataUse(Enum):
    """ Simple Enum class to indicate data usage context.
        Options are: TRAINING, VALIDATION, TEST
    """
    TRAINING = 1
    VALIDATION = 2
    TEST = 3

class DataHandler():
    """ Parent class for all MERIDIAN machine-learning models, which handles 
        input data for training, validation and testing of models.

        Args:
            train_x: numpy array
                Array in which each row holds an image.
            train_y: numpy array
                Array in which each row contains a label.
            validation_x: numpy array
                Array in which each row holds an image
            validation_y: numpy array
                Array in which each row contains a label
            test_x: numpy array
                Array in which each row holds an image
            test_y: numpy array
                Array in which each row contains a label
    """
    def __init__(self, train_x=None, train_y=None, validation_x=None, validation_y=None,
                 test_x=None, test_y=None, num_labels=None):

        self.num_labels = num_labels    

        self.images = {DataUse.TRAINING: None, DataUse.VALIDATION: None, DataUse.TEST: None}
        self.labels = {DataUse.TRAINING: None, DataUse.VALIDATION: None, DataUse.TEST: None}

        self._set_data(train_x, train_y, use=DataUse.TRAINING)        
        self._set_data(validation_x, validation_y, use=DataUse.VALIDATION)        
        self._set_data(test_x, test_y, use=DataUse.TEST)    

    def _set_data(self, x, y, use):
        """ Set data for specified use (training, validation, or test). 
            Replaces any existing data for that use type.

            Labels (y) can be provided as integers or encoded in 1-hot format.

            Args:
                x: numpy array
                    Array in which each row holds an image. 
                y: numpy array
                    Array in which each row contains a label.
                use: DataUse
                    Data use. Possible options are TRAINING, VALIDATION and TEST
        """
        if x is not None:
            check_data_sanity(x, y)

        x = self._ensure4d(x)
        y = self._ensure1hot(y)

        self.images[use] = x
        self.labels[use] = y

    def _add_data(self, x, y, use):
        """ Add data for specified use (training, validation, or test). 
            Will be appended to any existing data for that use type.

            Args:
                x: numpy array
                    Array in which each row holds an image. 
                y: numpy array
                    Array in which each row contains a label.
                use: DataUse
                    Data use. Possible options are TRAINING, VALIDATION and TEST
        """
        x0 = self.images[use]
        y0 = self.labels[use]
        if x0 is not None:
            x = self._ensure4d(x)
            x = np.append(x0, x, axis=0)
        if y0 is not None:
            y = self._ensure1hot(y)
            y = np.append(y0, y, axis=0)
        self._set_data(x=x, y=y, use=use)

    def _get_data(self, use):
        """ Get data of selected usage type

            Args:
                use: DataUse
                    Data use. Possible options are TRAINING, VALIDATION and TEST

            Returns:
                x: numpy array
                    Array in which each row holds an image.
                y: numpy array
                    Array in which each row contains a label
        """
        x = self.images[use]
        y = self.labels[use]
        return x, y

    def set_training_data(self, x, y):
        """ Set training data. Replaces any existing training data.

            Labels (y) can be provided as integers or encoded in 1-hot format.

            Args:
                x: numpy array
                    Array in which each row holds an image. 
                y: numpy array
                    Array in which each row contains a label

            Example:

                >>> from ketos.neural_networks.neural_networks import DataHandler
                >>> handler = DataHandler()
                >>> # create two 2x2 images
                >>> img1 = np.array([[1, 2],
                ...                 [3, 4]])
                >>> img2 = np.array([[5, 6],
                ...                 [7, 8]])
                >>> x = np.array([img1, img2]) # images
                >>> y = np.array([1, 0])       # labels
                >>> handler.set_training_data(x, y) # set the training data
                >>> xt, yt = handler.get_training_data() # get the training data
                >>> print(yt) # print the (1-hot encoded) labels
                [[0. 1.]
                 [1. 0.]]
        """
        self._set_data(x=x, y=y, use=DataUse.TRAINING)

    def add_training_data(self, x, y):
        """ Add training data. Will be appended to any existing training data.

            Labels (y) can be provided as integers or encoded in 1-hot format.

            Args:
                x: numpy array
                    Array in which each row holds an image. 
                y: numpy array
                    Array in which each row contains a label

            Example:

                >>> from ketos.neural_networks.neural_networks import DataHandler
                >>> handler = DataHandler()
                >>> # create two 2x2 images
                >>> img1 = np.array([[1, 2],
                ...                 [3, 4]])
                >>> img2 = np.array([[5, 6],
                ...                 [7, 8]])
                >>> x = np.array([img1, img2]) # images
                >>> y = np.array([1, 0])       # labels
                >>> handler.set_training_data(x, y) # set the training data
                >>> handler.add_training_data(x, y) # add more training data
                >>> xt, yt = handler.get_training_data() # get all training data
                >>> print(yt) # print the (1-hot encoded) labels
                [[0. 1.]
                 [1. 0.]
                 [0. 1.]
                 [1. 0.]]
        """
        self._add_data(x=x, y=y, use=DataUse.TRAINING)

    def get_training_data(self):
        """ Get training data.

            Returns:
                x: numpy array
                    Array in which each row holds an image.
                y: numpy array
                    Array in which each row contains a label
        """
        x, y = self._get_data(use=DataUse.TRAINING)
        return x, y

    def set_validation_data(self, x, y):
        """ Set validation data. Replaces any existing validation data.

            Labels (y) can be provided as integers or encoded in 1-hot format.

            Args:
                x: numpy array
                    Array in which each row holds an image. 
                y: numpy array
                    Array in which each row contains a label
        """
        self._set_data(x=x, y=y, use=DataUse.VALIDATION)

    def add_validation_data(self, x, y):
        """ Add validation data. Will be appended to any existing validation data.

            Args:
                x: numpy array
                    Array in which each row holds one image. 
                y: numpy array
                    Array in which each row contains the one hot encoded label
        """
        self._add_data(x=x, y=y, use=DataUse.VALIDATION)

    def get_validation_data(self):
        """ Get validation data.

            Returns:
                x: numpy array
                    Array in which each row holds an image.
                y: numpy array
                    Array in which each row contains a label
        """
        x, y = self._get_data(use=DataUse.VALIDATION)
        return x, y

    def set_test_data(self, x, y):
        """ Set test data. Replaces any existing test data.

            Args:
                x: numpy array
                    Array in which each row holds one image. 
                y: numpy array
                    Array in which each row contains the one hot encoded label
        """
        self._set_data(x=x, y=y, use=DataUse.TEST)

    def add_test_data(self, x, y):
        """ Add test data. Will be appended to any existing test data.

            Args:
                x: numpy array
                    Array in which each row holds one image. 
                y: numpy array
                    Array in which each row contains the one hot encoded label
        """
        self._add_data(x=x, y=y, use=DataUse.TEST)

    def get_test_data(self):
        """ Get test data.

            Returns:
                x: numpy array
                    Array in which each row holds an image.
                y: numpy array
                    Array in which each row contains a label
        """
        x, y = self._get_data(use=DataUse.TEST)
        return x, y

    def _ensure4d(self, x):
        """ Adds a 4th empty dimension to the numpy array

            If x is a list, it is converted to a numpy array

            Args:
                x: numpy array
                    Array in which each row holds an image. 

            Return:
                x: numpy array
                    Same as input array, but with an additional (empty) dimension 
        """
        if x is None:
            return x

        x = np.array(x)
        x = np.squeeze(x)

        if len(x.shape) == 0:
            x = np.array([x])

        if np.ndim(x) == 2:
            x = x[np.newaxis,:,:,]

        if np.ndim(x) == 3:
            x = x[:,:,:,np.newaxis]

        return x

    def _ensure1hot(self, y):
        """ Ensures that labels are 1-hot encoded

            If y is a list, it is converted to a numpy array

            Args:
                y: numpy array
                    Label array

            Return:
                y: numpy array
                    1-hot encoded label array
        """
        if y is None:
            return y

        y = np.array(y)
        y = np.squeeze(y)

        if len(y.shape) == 0:
            y = np.array([y])

        if np.ndim(y) == 1:
            if self.num_labels is None:
                depth = np.max(y) + 1 # figure it out from the data
            else:
                depth = self.num_labels

            y = to1hot(y, depth=depth) # use one-hot encoding

        return y
        