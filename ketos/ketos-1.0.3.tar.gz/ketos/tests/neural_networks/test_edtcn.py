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

""" Unit tests for the 'edtcn' module within the ketos library

"""
import pytest
import numpy as np
from ketos.neural_networks.edtcn import EDTCN


@pytest.mark.test_EDTCN
def test_initialize_EDTCN_with_default_constructor_and_default_args(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    _ = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y)

def test_create_EDTCN_network_with_default_args(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    net = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y)
    net.create()

def test_train_EDTCN_network_with_default_args(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    net = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y)
    net.create()
    net.train(num_epochs=1)

def test_create_EDTCN_network_with_max_len_not_divisible_by_four(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    net = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y, max_len=15)
    net.create()
    assert net.max_len == 16

def test_predict_labels_with_default_EDTCN_network(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    net = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y)
    net.create()
    net.train(num_epochs=1)
    N = 2
    p = net.get_predictions(x=train_x[0:N])
    assert len(p) == N

def test_get_class_weights_with_default_EDTCN_network(data_for_TCN):
    train_x, train_y, val_x, val_y, test_x, test_y = data_for_TCN
    net = EDTCN(train_x=train_x, train_y=train_y, validation_x=val_x, validation_y=val_y, test_x=test_x, test_y=test_y)
    net.create()
    net.train(num_epochs=1)
    N = 2
    w = net.get_class_weights(x=train_x[0:N])
    assert w.shape[0] == 2
    assert w[0,0]+w[0,1] == pytest.approx(1.0, abs=0.001)
    assert w[1,0]+w[1,1] == pytest.approx(1.0, abs=0.001)
