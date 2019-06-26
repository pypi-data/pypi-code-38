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

""" Unit tests for the data_feeding module within the ketos library
"""

import os
import pytest
import numpy as np
import pandas as pd
from tables import open_file
from ketos.data_handling.database_interface import open_table
from ketos.data_handling.data_feeding import ActiveLearningBatchGenerator, BatchGenerator
from ketos.neural_networks.neural_networks import class_confidences, predictions

current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_assets = os.path.join(os.path.dirname(current_dir),"assets")
path_to_tmp = os.path.join(path_to_assets,'tmp')


@pytest.mark.test_BatchGenerator
def test_one_batch():
    """ Test if one batch has the expected shape and contents
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') # create the database handle  
    train_data = open_table(h5, "/train/species1")

    five_specs = train_data[:5]['data']
    five_boxes = train_data[:5]['boxes']

    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=5, return_batch_ids=True) #create a batch generator 
    ids, X, Y = next(train_generator)
    assert ids == [0,1,2,3,4]
    assert X.shape == (5, 2413, 201)
    np.testing.assert_array_equal(X, five_specs)
    assert Y.shape == (5,)
    np.testing.assert_array_equal(Y, five_boxes)

    h5.close()


@pytest.mark.test_BatchGenerator
def test_labels_as_Y():
    """ Test if batch generator returns labels instead of boxes
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') # create the database handle  
    train_data = open_table(h5, "/train/species1")
    
    five_labels = train_data[:5]['labels']

    train_generator = BatchGenerator(hdf5_table=train_data, y_field='labels', batch_size=5, return_batch_ids=False) #create a batch generator 
    _, Y = next(train_generator)
    np.testing.assert_array_equal(Y, five_labels)

    h5.close()
    

@pytest.mark.test_BatchGenerator
def test_batch_sequence_same_as_db():
    """ Test if batches are generated with instances in the same order as they appear in the database
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")

    ids_in_db = train_data[:]['id']
    train_generator = BatchGenerator(hdf5_table=train_data, x_field='id', batch_size=3, return_batch_ids=True) #create a batch generator 

    for i in range(3):
        ids, X, _ = next(train_generator)
        np.testing.assert_array_equal(X, ids_in_db[i*3: i*3+3])
        assert ids == list(range(i*3, i*3+3))
    
    h5.close()


@pytest.mark.test_BatchGenerator
def test_last_batch():
    """ Test if last batch has the expected number of instances
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")

    ids_in_db = train_data[:]['id']
    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=6, return_batch_ids=True) #create a batch generator 
    #First batch
    ids, X, _ = next(train_generator)
    assert ids == [0,1,2,3,4,5]
    assert X.shape == (6, 2413, 201)
    #Second batch
    ids, X, _ = next(train_generator)
    assert ids == [6,7,8,9,10,11]
    assert X.shape == (6, 2413, 201)
    #last batch
    ids, X, _ = next(train_generator)
    assert ids == [12,13,14]
    assert X.shape == (3, 2413, 201)

    h5.close()

@pytest.mark.test_BatchGenerator
def test_use_only_subset_of_data():
    """ Test that only the indices specified are used
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")

    train_generator = BatchGenerator(hdf5_table=train_data, indices=[1,3,5,7,9,11,13], batch_size=4, return_batch_ids=True) #create a batch generator 
    #First batch
    ids, X, _ = next(train_generator)
    assert ids == [1,3,5,7]
    #Second batch
    ids, X, _ = next(train_generator)
    assert ids == [9,11,13]

    h5.close()

@pytest.mark.test_BatchGenerator
def test_multiple_epochs():
    """ Test if batches are as expected after the first epoch
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")

    ids_in_db = train_data[:]['id']
    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=6, return_batch_ids=True) #create a batch generator 
    #Epoch 0, batch 0
    ids, X, _ = next(train_generator)
    assert ids == [0,1,2,3,4,5]
    assert X.shape == (6, 2413, 201)
    #Epoch 0, batch 1
    ids, X, _ = next(train_generator)
    assert ids == [6,7,8,9,10,11]
    assert X.shape == (6, 2413, 201)
    #Epoch 0 batch2
    ids, X, _ = next(train_generator)
    assert ids == [12,13,14]
    assert X.shape == (3, 2413, 201)

    #Epoch 1, batch 0
    ids, X, _ = next(train_generator)
    assert ids == [0,1,2,3,4,5]
    assert X.shape == (6, 2413, 201)

    h5.close()

@pytest.mark.test_BatchGenerator
def test_load_from_memory():
    """ Test if batch generator can work with data loaded from memory
    """
    x = np.ones(shape=(15,32,16))
    y = np.zeros(shape=(15))

    generator = BatchGenerator(x=x, y=y, batch_size=6, return_batch_ids=True) #create a batch generator 

    #Epoch 0, batch 0
    ids, X, _ = next(generator)
    assert ids == [0,1,2,3,4,5]
    assert X.shape == (6, 32, 16)
    #Epoch 0, batch 1
    ids, X, _ = next(generator)
    assert ids == [6,7,8,9,10,11]
    assert X.shape == (6, 32, 16)
    #Epoch 0 batch2
    ids, X, _ = next(generator)
    assert ids == [12,13,14]
    assert X.shape == (3, 32, 16)

    #Epoch 1, batch 0
    ids, X, _ = next(generator)
    assert ids == [0,1,2,3,4,5]
    assert X.shape == (6, 32, 16)

@pytest.mark.test_BatchGenerator
def test_shuffle():
    """Test shuffle argument.
        Instances should be shuffled before divided into batches, but the order should be consistent across epochs if
        'refresh_on_epoch_end' is False.
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")


    ids_in_db = train_data[:]['id']
    np.random.seed(100)
    
    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=6, return_batch_ids=True, shuffle=True) #create a batch generator 

    for epoch in range(5):
        #batch 0
        ids, X, _ = next(train_generator)
        assert ids == [9, 1, 12, 13, 6, 10]
        assert X.shape == (6, 2413, 201)
        #batch 1
        ids, X, _ = next(train_generator)
        assert ids == [5, 2, 4, 0, 11, 7]
        assert X.shape == (6, 2413, 201)
        #batch 2
        ids, X, _ = next(train_generator)
        assert ids ==  [3, 14, 8]
        assert X.shape == (3, 2413, 201)
    
    h5.close()


@pytest.mark.test_BatchGenerator
def test_refresh_on_epoch_end():
    """ Test if batches are generated with randomly selected instances for each epoch
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') #create the database handle  
    train_data = open_table(h5, "/train/species1")

    ids_in_db = train_data[:]['id']
    np.random.seed(100)
    
    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=6, return_batch_ids=True, shuffle=True, refresh_on_epoch_end=True) #create a batch generator 

    expected_ids = {'epoch_1':([9, 1, 12, 13, 6, 10],[5, 2, 4, 0, 11, 7],[3, 14, 8]),
                     'epoch_2': ([0, 2, 1, 14, 10, 3],[13, 12, 5, 8, 11, 7],[6, 4, 9]),    
                     'epoch_3': ([7, 13, 1, 0, 11, 9],[5, 8, 2, 12, 4, 6],[10, 14, 3])}
                     
    for epoch in ['epoch_1', 'epoch_2', 'epoch_3']:
        #batch 0
        ids, X, _ = next(train_generator)
        print(epoch)
        assert ids == expected_ids[epoch][0]
        #batch 1
        ids, X, _ = next(train_generator)
        assert ids == expected_ids[epoch][1]
        #batch 2
        ids, X, _ = next(train_generator)
        assert ids == expected_ids[epoch][2]
    
    h5.close()

@pytest.mark.test_BatchGenerator
def test_instance_function():
    """ Test if the function passed as 'instance_function' is applied to the batch
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r') # create the database handle  
    train_data = open_table(h5, "/train/species1")

    def apply_to_batch(X,Y):
        X = np.mean(X, axis=(1,2))
        return (X, Y)

    train_generator = BatchGenerator(hdf5_table=train_data, batch_size=5, return_batch_ids=True, instance_function=apply_to_batch) #create a batch generator 
    _, X, Y = next(train_generator)
    assert X.shape == (5,)
    assert X[0] == pytest.approx(7694.1147, 0.1)
    assert Y.shape == (5,)
    
    h5.close()


@pytest.mark.test_ActiveLearningBatchGenerator
def test_active_learning_batch_generator_max_keep_zero():
    """ Test can start first training session
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r')  
    data = open_table(h5, "/train/species1")

    specs = data[:]['data']
    labels = data[:]['labels']

    a = ActiveLearningBatchGenerator(table=data, session_size=6, batch_size=2, return_indices=True)

    # get 1st batch generator
    generator = next(a)

    # get 1st batch
    ids, X, Y = next(generator)
    assert ids == [0,1]
    assert X.shape == (2, 2413, 201)
    np.testing.assert_array_equal(X, specs[:2])
    assert len(Y) == 2
    assert Y == [1,1]

    # get 2nd batch
    ids, X, Y = next(generator)
    assert ids == [2,3]
    assert X.shape == (2, 2413, 201)
    np.testing.assert_array_equal(X, specs[2:4])
    assert len(Y) == 2
    assert Y == [1,1]

    # get 3rd and 4th batch
    ids, _, _ = next(generator) 
    assert ids == [4,5]
    ids, _, _ = next(generator) 
    assert ids == [0,1]

    # get 2nd batch generator
    generator = next(a)

    # get batches
    ids, _, _ = next(generator) 
    assert ids == [6,7]
    ids, _, _ = next(generator) 
    assert ids == [8,9]
    ids, _, _ = next(generator) 
    assert ids == [10,11]
    ids, _, _ = next(generator) 
    assert ids == [6,7]

    # get 3rd batch generator
    generator = next(a)

    # get batches
    ids, _, _ = next(generator) 
    assert ids == [12,13]
    ids, _, _ = next(generator) 
    assert ids == [14,0]
    ids, _, _ = next(generator) 
    assert ids == [1,2]

    h5.close()


@pytest.mark.test_ActiveLearningBatchGenerator
def test_active_learning_batch_generator_max_keep_nonzero():
    """ Test can start first training session
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r')  
    data = open_table(h5, "/train/species1")

    a = ActiveLearningBatchGenerator(table=data, session_size=7, batch_size=3, max_keep=0.3, return_indices=True)

    generator = next(a)

    ids, _, _ = next(generator)
    assert ids == [0,1,2]
    ids, _, _ = next(generator)
    assert ids == [3,4,5]
    ids, _, _ = next(generator)
    assert ids == [6]

    generator = next(a)

    ids, _, Y = next(generator)
    assert ids == [7,8,9]
    assert Y == [1,1,1]
    a.update_performance(indices=[7,8,9], predictions=[1,1,1], confidences=[1.0,1.0,1.0])

    ids, _, Y = next(generator)
    assert ids == [10,11,12]
    assert Y == [1,1,1]
    a.update_performance(indices=[10,11,12], predictions=[1,1,1], confidences=[1.0,1.0,1.0])

    ids, _, Y = next(generator)
    assert ids == [13]
    assert Y == 1
    a.update_performance(indices=[13], predictions=[0], confidences=[1.0])

    generator = next(a)

    ids1, _, Y = next(generator)
    assert Y == [1,1,1]
    a.update_performance(indices=ids1, predictions=[1,0,0])

    ids2, _, Y = next(generator)
    assert Y == [1,1,1]
    a.update_performance(indices=ids2, predictions=[0,0,0])

    ids3, _, Y = next(generator)
    assert Y == 1
    a.update_performance(indices=ids3, predictions=[1])

    ids = np.concatenate((ids1, ids2, ids3))
    assert 13 in ids

    wrong_ids = [ids1[1], ids1[2], ids2[0], ids2[1], ids2[2]]

    generator = next(a)

    ids1, _, _ = next(generator)
    ids2, _, _ = next(generator)
    ids3, _, _ = next(generator)
    ids = np.concatenate((ids1, ids2, ids3))

    # check how many of the wrong predictiosn were kept
    # since max_keep = 0.3 and session_size = 7, it should be int(0.3*7) = 2
    num_keep = 0
    for id in wrong_ids:
        num_keep += (id in ids)

    assert num_keep == 2

    h5.close()


@pytest.mark.test_ActiveLearningBatchGenerator
def test_active_learning_batch_generator_load_from_memory():
    """ Test can start first and second training session
    """
    x = np.ones(shape=(15,32,16))
    y = np.zeros(shape=(15))

    a = ActiveLearningBatchGenerator(x=x, y=y, session_size=7, batch_size=3, return_indices=True)

    generator = next(a)

    ids, _, _ = next(generator)
    assert ids == [0,1,2]
    ids, _, _ = next(generator)
    assert ids == [3,4,5]
    ids, _, _ = next(generator)
    assert ids == [6]

    generator = next(a)

    ids, _, _ = next(generator)
    assert ids == [7,8,9]


@pytest.mark.test_ActiveLearningBatchGenerator
def test_active_learning_batch_generator_splits_into_training_and_validation():
    """ Test can split into training and validation data
    """
    h5 = open_file(os.path.join(path_to_assets, "15x_same_spec.h5"), 'r')  
    data = open_table(h5, "/train/species1")

    specs = data[:]['data']
    labels = data[:]['labels']

    a = ActiveLearningBatchGenerator(table=data, session_size=6, batch_size=2, num_labels=2,\
        return_indices=True, seed=1, val_frac=0.2, convert_to_one_hot=True)

    assert len(a.val_indices) == 3

    generator = next(a)
    indices = np.concatenate((generator.entry_indices, a.val_indices))

    generator = next(a)
    indices = np.concatenate((generator.entry_indices, indices))

    indices = np.sort(indices)
    indices = np.unique(indices)

    assert np.all(indices == np.arange(15))

    idx, X, Y = a.get_validation_data()
    assert np.all(idx == a.val_indices)

    assert Y.shape[0] == 3
    assert Y.shape[1] == 2

    h5.close()
