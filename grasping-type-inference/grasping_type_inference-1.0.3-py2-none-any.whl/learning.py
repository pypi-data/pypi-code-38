# Copyright 2018 Institute for Artificial Intelligence - University of Bremen
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


def train_all_grasping_mlns(path_to_training_files, path_to_mln_files=MLN_PATH):
    for training_file in os.listdir(path_to_training_files):
        if training_file.endswith('.db'):
            path_mln_training_file = os.path.join(path_to_training_files, training_file)
            mln_training_file_content = None

            with open(path_mln_training_file) as mln_training_file:
                mln_training_file_content = mln_training_file.read()

            #BOWL.train.db
            object_type = training_file.split('.')[0].lower()
            grasping_object_type_mln_name = 'grasping_{}.pracmln'.format(object_type)
            path_to_grasping_type_mln = os.path.join(path_to_mln_files, grasping_object_type_mln_name)
            grasping_object_type_mln = MarkovLogicNetwork(path_to_grasping_type_mln)
            print 'Learning {} ...'.format(grasping_object_type_mln_name)
            grasping_object_type_mln.learn(mln_training_file_content)
            print 'Learning is done'
            print ''

