# -*- coding: utf-8 -*-

# Copyright © 2018 Institute for Artificial Intelligence - University of Bremen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from grasping_type_inference.definitions import ROOT_DIR
from high_level_markov_logic_network.markov_logic_network import MarkovLogicNetwork

MLN_PATH = os.path.join(ROOT_DIR, 'mln')


def set_mln_path(mln_path):
    global MLN_PATH
    MLN_PATH = mln_path


def __get_grasping_type_mln__():
    path_to_grasping_type_mln = os.path.join(MLN_PATH, 'grasping_type.pracmln')

    return MarkovLogicNetwork(path_to_grasping_type_mln)


def __get_grasping_mln_selector_mln__():
    path_to_grasping_mln_selector_mln = os.path.join(MLN_PATH, 'grasping_mln_selector.pracmln')

    return MarkovLogicNetwork(path_to_grasping_mln_selector_mln)


def load_grasping_mln(mln_filename):
    path_to_grasping_mln = os.path.join(MLN_PATH, mln_filename)

    return MarkovLogicNetwork(path_to_grasping_mln)


def get_grasping_mln_selector_mln():
    path_to_grasping_mln_selector_mln = os.path.join(MLN_PATH, 'grasping_mln_selector.pracmln')
    return MarkovLogicNetwork(path_to_grasping_mln_selector_mln)





