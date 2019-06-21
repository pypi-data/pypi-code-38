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

""" Unit tests for the 'cnn' module within the ketos library
"""

import pytest
import os
import tables
import numpy as np
import ketos.data_handling.data_handling as dh
import ketos.data_handling.database_interface as di
from ketos.data_handling.data_feeding import BatchGenerator
from ketos.neural_networks.cnn import BasicCNN, ConvParams
from tensorflow import reset_default_graph

current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_assets = os.path.join(os.path.dirname(current_dir),"assets")
path_to_tmp = os.path.join(path_to_assets,'tmp')

@pytest.mark.test_BasicCNN
def test_initialize_BasicCNN_with_default_constructor_and_default_args(database_prepared_for_NN):
    d = database_prepared_for_NN
    train_x = d["train_x"]
    train_y = d["train_y"]
    _ = BasicCNN(train_x=train_x, train_y=train_y, verbosity=0)
    reset_default_graph()

@pytest.mark.test_BasicCNN
def test_train_BasicCNN_with_default_args(database_prepared_for_NN):
    d = database_prepared_for_NN
    train_x = d["train_x"]
    train_y = d["train_y"]
    validation_x = d["validation_x"]
    validation_y = d["validation_y"]
    test_x = d["test_x"]
    test_y = d["test_y"]
    network = BasicCNN(train_x=train_x, train_y=train_y, validation_x=validation_x, validation_y=validation_y, test_x=test_x, test_y=test_y, num_labels=2, verbosity=0)
    _ = network.create()
    network.train()
    reset_default_graph()

@pytest.mark.test_BasicCNN
def test_train_BasicCNN_with_default_args2(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    train_x = d["train_x"]
    train_y = d["train_y"]
    validation_x = d["validation_x"]
    validation_y = d["validation_y"]
    test_x = d["test_x"]
    test_y = d["test_y"]
    network = BasicCNN(train_x=train_x, train_y=train_y, validation_x=validation_x, validation_y=validation_y, test_x=test_x, test_y=test_y, num_labels=2, verbosity=0)
    _ = network.create()
    network.train()
    reset_default_graph()

@pytest.mark.test_BasicCNN
def test_train_BasicCNN_with_train_batch_generator(database_prepared_for_NN_2_classes):
    """ Test if batch generator returns labels instead of boxes
    """
    database = tables.open_file(os.path.join(path_to_assets,"humpback.h5"), 'r')
    train_data = di.open_table(database, "/train/mel_specs" )
    val_data = di.open_table(database, "/validation/mel_specs" )
    test_data = di.open_table(database, "/test/mel_specs")
    
    image_shape = train_data[0]['data'].shape
    def parse_y(y):
        labels=list(map(lambda l: dh.to1hot(di.parse_labels(l)[0], depth=2), y ))
        return np.array(labels)


    def apply_to_batch(X,Y):
        Y = parse_y(Y)
        return (X,Y)
    
    validation_x = val_data[:5]['data']
    validation_y = parse_y(val_data[:5]['labels'])
    
    train_generator = BatchGenerator(hdf5_table=train_data, y_field='labels', batch_size=5, return_batch_ids=False, instance_function=apply_to_batch) 
    
       
    network = BasicCNN(image_shape=image_shape, validation_x=validation_x, validation_y=validation_y, num_epochs=2, num_labels=2, seed=123, batch_size=5, verbosity=0 )

    conv_params = [ConvParams(name='conv_1', n_filters=32, filter_shape=[2,8]),
         ConvParams(name='conv_2', n_filters=64, filter_shape=[30,8])]

    _ = network.create(conv_params=conv_params, dense_size=[512])
    network.train(train_batch_gen=train_generator)
    # network.train()
    reset_default_graph()

@pytest.mark.test_BasicCNN
def test_load_BasicCNN_model(database_prepared_for_NN_2_classes, trained_BasicCNN):
    d = database_prepared_for_NN_2_classes
    train_x = d["train_x"]
    train_y = d["train_y"]
    validation_x = d["validation_x"]
    validation_y = d["validation_y"]
    test_x = d["test_x"]
    test_y = d["test_y"]
    network = BasicCNN(train_x=train_x, train_y=train_y, validation_x=validation_x, validation_y=validation_y, test_x=test_x, test_y=test_y, num_labels=2, verbosity=0)
    path_to_meta, path_to_saved_model, test_acc = trained_BasicCNN
    _ = network.load(path_to_meta, path_to_saved_model)
    assert test_acc == network.accuracy_on_test()
    reset_default_graph()
    
@pytest.mark.test_BasicCNN
def test_compute_class_weights_with_BasicCNN(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    network = BasicCNN(train_x=x, train_y=y, num_labels=2, verbosity=0, seed=41)
    _ = network.create()
    network.train()
    img = np.zeros((20, 20))
    result = network.get_class_weights(x=[img])
    weights = result[0]
    assert weights[0] + weights[1] == pytest.approx(1.000, abs=0.001)
    reset_default_graph()

@pytest.mark.test_BasicCNN
def test_compute_features_with_BasicCNN(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    x = d["train_x"]
    y = d["train_y"]
    network = BasicCNN(train_x=x, train_y=y,  num_labels=2, verbosity=0, seed=41)
    _ = network.create()
    network.train()
    img = np.zeros((20, 20))
    result = network.get_features(x=[img], layer_name='dense_1')
    f = result[0]
    assert f.shape == (512,)
    reset_default_graph()
