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

import pytest
import datetime
import os
import numpy as np
import scipy.signal as sg
import pandas as pd
import ketos.audio_processing.audio_processing as ap
from ketos.neural_networks.cnn import BasicCNN
from ketos.data_handling.data_handling import to1hot
import ketos.audio_processing.audio as aud
from tensorflow import reset_default_graph

path_to_assets = os.path.join(os.path.dirname(__file__),"assets")


@pytest.fixture
def sine_wave():
    sampling_rate = 44100
    frequency = 2000
    duration = 3
    x = np.arange(duration * sampling_rate)

    signal = 32600*np.sin(2 * np.pi * frequency * x / sampling_rate) 

    return sampling_rate, signal


@pytest.fixture
def square_wave():
    sampling_rate = 44100
    frequency = 2000
    duration = 3
    x = np.arange(duration * sampling_rate)

    signal = 32600 * sg.square(2 * np.pi * frequency * x / sampling_rate) 

    return sampling_rate, signal

@pytest.fixture
def sawtooth_wave():
    sampling_rate = 44100
    frequency = 2000
    duration = 3
    x = np.arange(duration * sampling_rate)

    signal = 32600 * sg.sawtooth(2 * np.pi * frequency * x / sampling_rate) 

    return sampling_rate, signal

@pytest.fixture
def const_wave():
    sampling_rate = 44100
    duration = 3
    x = np.arange(duration * sampling_rate)
    signal = np.ones(len(x))

    return sampling_rate, signal


@pytest.fixture
def sine_wave_file(sine_wave):
    """Create a .wav with the 'sine_wave()' fixture
    
       The file is saved as tests/assets/sine_wave.wav.
       When the tests using this fixture are done, 
       the file is deleted.


       Yields:
            wav_file : str
                A string containing the path to the .wav file.
    """
    wav_file = os.path.join(path_to_assets, "sine_wave.wav")
    rate, sig = sine_wave
    ap.wave.write(wav_file, rate=rate, data=sig)
    
    yield wav_file
    os.remove(wav_file)


@pytest.fixture
def square_wave_file(square_wave):
    """Create a .wav with the 'square_wave()' fixture
    
       The file is saved as tests/assets/square_wave.wav.
       When the tests using this fixture are done, 
       the file is deleted.


       Yields:
            wav_file : str
                A string containing the path to the .wav file.
    """
    wav_file =  os.path.join(path_to_assets, "square_wave.wav")
    rate, sig = square_wave
    ap.wave.write(wav_file, rate=rate, data=sig)

    yield wav_file
    os.remove(wav_file)


@pytest.fixture
def sawtooth_wave_file(sawtooth_wave):
    """Create a .wav with the 'sawtooth_wave()' fixture
    
       The file is saved as tests/assets/sawtooth_wave.wav.
       When the tests using this fixture are done, 
       the file is deleted.


       Yields:
            wav_file : str
                A string containing the path to the .wav file.
    """
    wav_file =  os.path.join(path_to_assets, "sawtooth_wave.wav")
    rate, sig = sawtooth_wave
    ap.wave.write(wav_file, rate=rate, data=sig)

    yield wav_file
    os.remove(wav_file)


@pytest.fixture
def const_wave_file(const_wave):
    """Create a .wav with the 'const_wave()' fixture
    
       The file is saved as tests/assets/const_wave.wav.
       When the tests using this fixture are done, 
       the file is deleted.


       Yields:
            wav_file : str
                A string containing the path to the .wav file.
    """
    wav_file =  os.path.join(path_to_assets, "const_wave.wav")
    rate, sig = const_wave
    ap.wave.write(wav_file, rate=rate, data=sig)

    yield wav_file
    os.remove(wav_file)

@pytest.fixture
def image_2x2():
    image = np.array([[1,2],[3,4]], np.float32)
    return image

@pytest.fixture
def image_3x3():
    image = np.array([[1,2,3],[4,5,6],[7,8,9]], np.float32)
    return image

@pytest.fixture
def image_ones_10x10():
    image = np.ones(shape=(10,10))
    return image

@pytest.fixture
def image_zeros_and_ones_10x10():
    image = np.ones(shape=(10,10))
    for i in range(10):
        for j in range(5):
            image[i,j] = 0
    return image

@pytest.fixture
def datebase_with_one_image_col_and_one_label_col(image_2x2):
    d = {'image': [image_2x2], 'label': [1]}
    df = pd.DataFrame(data=d)
    return df


@pytest.fixture
def datebase_with_one_image_col_and_no_label_col(image_2x2):
    d = {'image': [image_2x2]}
    df = pd.DataFrame(data=d)
    return df


@pytest.fixture
def datebase_with_two_image_cols_and_one_label_col(image_2x2):
    d = {'image1': [image_2x2], 'image2': [image_2x2], 'label': [1]}
    df = pd.DataFrame(data=d)
    return df


@pytest.fixture
def database_prepared_for_NN(image_2x2):
    d = {'image': [image_2x2, image_2x2, image_2x2, image_2x2, image_2x2, image_2x2], 'label': [0,0,0,0,0,0]}
    df = pd.DataFrame(data=d)
    divisions = {"train":(0,3),"validation":(3,4),"test":(4,6)}
    prepared = prepare_database(df, "image", "label", divisions)     
    return prepared

@pytest.fixture
def database_prepared_for_NN_2_classes():
    img1 = np.zeros((20, 20))
    img2 = np.ones((20, 20))
    d = {'image': [img1, img2, img1, img2, img1, img2,
                   img1, img2, img1, img2, img1, img2,
                   img1, img2, img1, img2, img1, img2,
                   img1, img2, img1, img2, img1, img2],
         'label': [0, 1, 0, 1, 0, 1,
                   0, 1, 0, 1, 0, 1,
                   0, 1, 0, 1, 0, 1,
                   0, 1, 0, 1, 0, 1]}
    database = pd.DataFrame(data=d)
    divisions= {"train":(0,12),
                "validation":(12,18),
                "test":(18,len(database))}
    prepared = prepare_database(database=database,x_column="image",y_column="label",
                                divisions=divisions)    
    return prepared


@pytest.fixture
def trained_BasicCNN(database_prepared_for_NN_2_classes):
    d = database_prepared_for_NN_2_classes
    path_to_saved_model = os.path.join(path_to_assets, "saved_models")
    path_to_meta = os.path.join(path_to_saved_model, "trained_BasicCNN")         
    train_x = d["train_x"]
    train_y = d["train_y"]
    validation_x = d["validation_x"]
    validation_y = d["validation_y"]
    test_x = d["test_x"]
    test_y = d["test_y"]
    network = BasicCNN(train_x=train_x, train_y=train_y, validation_x=validation_x, validation_y=validation_y, test_x=test_x, test_y=test_y, batch_size=1, num_labels=2)
    tf_nodes = network.create()
    network.set_tf_nodes(tf_nodes)
    network.train()
    network.save(path_to_meta)
    test_acc = network.accuracy_on_test()
    meta = path_to_meta + ".meta"
    reset_default_graph()
    return meta, path_to_saved_model, test_acc

@pytest.fixture
def sine_audio(sine_wave):
    rate, data = sine_wave
    today = datetime.datetime.today()
    a = aud.TimeStampedAudioSignal(rate=rate, data=data, time_stamp=today, tag="audio")
    return a

@pytest.fixture
def sine_audio_without_time_stamp(sine_wave):
    rate, data = sine_wave
    a = aud.AudioSignal(rate=rate, data=data)
    return a
    
@pytest.fixture
def data_classified_by_nn():
    x = [1, 2, 3, 4, 5, 6] # input data
    x = np.array(x)
    y = [0, 1, 0, 1, 0, 1] # labels
    y = np.array(y)
    w = [[0.8, 0.2], [0.1, 0.9], [0.96, 0.04], [0.49, 0.51], [0.45, 0.55], [0.60, 0.40]] # class weights computed by NN
    w = np.array(w)
    return x,y,w

@pytest.fixture
def data_for_TCN():
    fv0 = np.zeros(64)
    fv1 = np.ones(64)
    x_train = np.array([fv0, fv1, fv0, fv1, fv0, fv1, fv0, fv1, fv0, fv1])
    y_train = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    x_val = np.array([fv0, fv1, fv0, fv1])
    y_val = np.array([0, 1, 0, 1])
    x_test = np.array([fv0, fv1, fv0, fv1])
    y_test = np.array([0, 1, 0, 1])
    return x_train, y_train, x_val, y_val, x_test, y_test
    

def encode_database(database, x_column, y_column):
    image_shape = database[x_column][0].shape
    depth = database[y_column].max() + 1 #number of classes
    database["one_hot_encoding"] = database[y_column].apply(to1hot,depth=depth)
    database["x_flatten"] = database[x_column].apply(lambda x: x.flatten())
    return database, image_shape

def split_database(database, divisions):
    train_data = database[divisions["train"][0]:divisions["train"][1]]
    validation_data = database[divisions["validation"][0]:divisions["validation"][1]]
    test_data = database[divisions["test"][0]:divisions["test"][1]]
    datasets = {"train": train_data,
                "validation": validation_data,
                "test": test_data}
    return datasets

def stack_dataset(dataset, input_shape):
    x = np.vstack(dataset.x_flatten).reshape(dataset.shape[0], input_shape[0], input_shape[1],1).astype(np.float32)
    y = np.vstack(dataset.one_hot_encoding)
    stacked_dataset = {'x': x,
                       'y': y}
    return stacked_dataset

def prepare_database(database, x_column, y_column, divisions):
    encoded_data, input_shape = encode_database(database=database, x_column=x_column, y_column=y_column)
    datasets = split_database(database=encoded_data, divisions=divisions)
    stacked_train = stack_dataset(dataset=datasets["train"], input_shape=input_shape)
    stacked_validation = stack_dataset(dataset=datasets["validation"], input_shape=input_shape)
    stacked_test = stack_dataset(dataset=datasets["test"], input_shape=input_shape)
    stacked_datasets = {"train_x": stacked_train["x"],
                        "train_y": stacked_train["y"],
                        "validation_x": stacked_validation["x"],
                        "validation_y": stacked_validation["y"],
                        "test_x": stacked_test["x"],
                        "test_y": stacked_test["y"]}
    return stacked_datasets
