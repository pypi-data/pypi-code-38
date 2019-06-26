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

""" Unit tests for the 'neural_networks' module within the ketos library
"""

import pytest
import numpy as np
import pandas as pd
import ketos.data_handling.data_handling as dh
from ketos.neural_networks.neural_networks import DataHandler, DataUse, class_confidences
from tensorflow import reset_default_graph


@pytest.mark.test_DataHandler
def test_initialize_DataHandler(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    print(x.shape)
    print(y.shape)
    _ = DataHandler(train_x=x, train_y=y)

@pytest.mark.test_DataHandler
def test_set_data_to_DataHandler(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    network = DataHandler(train_x=x, train_y=y)
    # set training data
    network.set_training_data(x=x, y=y)
    assert np.all(x == network.images[DataUse.TRAINING])
    assert np.all(y == network.labels[DataUse.TRAINING])
    # set validation data
    network.set_validation_data(x=x, y=y)
    assert np.all(x == network.images[DataUse.VALIDATION])
    assert np.all(y == network.labels[DataUse.VALIDATION])
    # set test data
    network.set_test_data(x=x, y=y)
    assert np.all(x == network.images[DataUse.TEST])
    assert np.all(y == network.labels[DataUse.TEST])    

@pytest.mark.test_DataHandler
def test_add_data_to_DataHandler(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    network = DataHandler(train_x=x, train_y=y)
    # add training data
    network.add_training_data(x=x, y=y)
    assert 2 * x.shape[0] == network.images[DataUse.TRAINING].shape[0]
    assert x.shape[1:] == network.images[DataUse.TRAINING].shape[1:]
    assert 2 * y.shape[0] == network.labels[DataUse.TRAINING].shape[0]
    assert y.shape[1:] == network.labels[DataUse.TRAINING].shape[1:]
    
@pytest.mark.test_DataHandler
def test_get_data_from_DataHandler(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    network = DataHandler(train_x=x, train_y=y)
    # get training data
    xx, yy = network.get_training_data()
    assert x.shape == xx.shape
    assert y.shape == yy.shape

@pytest.mark.test_class_confidences
def test_class_confidences(data_classified_by_nn):
    _,_,w = data_classified_by_nn
    conf = class_confidences(class_weights=w)
    assert len(conf) == 6
    assert conf[0] == pytest.approx(0.6, abs=0.001)
    assert conf[1] == pytest.approx(0.8, abs=0.001)
