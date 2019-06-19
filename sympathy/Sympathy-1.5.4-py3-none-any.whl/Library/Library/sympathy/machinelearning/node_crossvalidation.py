# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import numpy as np
import sklearn.model_selection
import numpy.ma as ma

from sympathy.api import node
from sympathy.api.nodeconfig import Port
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags
from sympathy.api.nodeconfig import TemplateTypes as tmpl

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract

from sylib.machinelearning.utility import array_to_table
from sylib.machinelearning.utility import table_to_array


class CrossVal_SuperNode(node.Node):
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.Partitioning)

    inputs = Ports([
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y')])
    outputs = Ports([
        Port.Custom('[(table, table)]', 'out', name='out')
    ])

    def use_model_select(self, node_context, ms, unitary_y=False):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        out = node_context.output['out']
        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)

        if unitary_y:
            Y_split = Y[:, 0].reshape(Y.shape[0])
        else:
            Y_split = Y

        for n, (train_idx, test_idx) in enumerate(ms.split(X=X, y=Y_split)):
            tbl = out.create()
            tbl[0].set_column_from_array("train", np.array(train_idx))
            tbl[1].set_column_from_array("test", np.array(test_idx))
            tbl[0].set_name("split {} train".format(n))
            tbl[1].set_name("split {} test".format(n))
            out.append(tbl)


class CrossVal_GroupSuperNode(node.Node):
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.Partitioning)

    inputs = Ports([
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y'),
        Port.Table('G', name='G')])
    outputs = Ports([
        Port.Custom('[(table, table)]', 'out', name='out')
    ])

    def use_model_select_group(self, node_context, ms, unitary_y=False):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        G_tbl = node_context.input['G']
        out = node_context.output['out']
        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)
        G = table_to_array(G_tbl)

        if unitary_y:
            Y_split = Y[:, 0].reshape(Y.shape[0])
        else:
            Y_split = Y

        for n, (train_idx, test_idx) in enumerate(
                ms.split(X=X, y=Y_split, groups=G[:, 0])):
            tbl = out.create()
            tbl[0].set_column_from_array("train", np.array(train_idx))
            tbl[1].set_column_from_array("test", np.array(test_idx))
            tbl[0].set_name("split {} train".format(n))
            tbl[1].set_name("split {} test".format(n))
            out.append(tbl)


class CrossVal_KFold(CrossVal_SuperNode):
    name = 'K-fold Cross Validation'
    icon = 'Kfold.svg'
    description = 'Gives splits for K-fold cross validation'
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_kfold'

    parameters = node.parameters()
    parameters.set_integer('n_splits', value=3, label='Number of splits',
                           description='Number of folds, must be atleast 2')
    parameters.set_boolean('shuffle', value=True, label='Shuffle',
                           description='Shuffle the data before splitting')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        CrossVal_SuperNode.inputs, CrossVal_SuperNode.outputs)

    def execute(self, node_context):
        ms = sklearn.model_selection.KFold(
            n_splits=node_context.parameters['n_splits'].value,
            shuffle=node_context.parameters['shuffle'].value)
        self.use_model_select(node_context, ms)


class CrossVal_StratifiedKFold(CrossVal_SuperNode):
    name = 'Stratified K-fold cross validation'
    icon = 'Kfold.svg'
    description = 'Gives splits for stratified K-fold cross validation'
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_stratifiedkfold'

    parameters = node.parameters()
    parameters.set_integer('n_splits', value=3, label='Number of splits',
                           description='Number of folds, must be atleast 2')
    parameters.set_boolean('shuffle', value=True, label='Shuffle',
                           description='Shuffle the data before splitting')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        CrossVal_SuperNode.inputs, CrossVal_SuperNode.outputs)

    def execute(self, node_context):
        ms = sklearn.model_selection.StratifiedKFold(
            n_splits=node_context.parameters['n_splits'].value,
            shuffle=node_context.parameters['shuffle'].value)
        self.use_model_select(node_context, ms, unitary_y=True)


class CrossVal_TimeSeriesSplit(CrossVal_SuperNode):
    name = 'Time Series K-fold Based Cross Validation'
    icon = 'timeseries_split.svg'
    description = (
        'Time series cross-validator based on K-fold suitable for'
        'time serie data. In the kth split, it returns first k folds as '
        'training set and the (k+1)th fold as test set.')
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_timeseries'

    parameters = node.parameters()
    parameters.set_integer('n_splits', value=3, label='Number of splits',
                           description='Number of folds, must be atleast 2')
    parameters.set_boolean('shuffle', value=False, label='Shuffle',
                           description='Shuffle the data before splitting')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        CrossVal_SuperNode.inputs, CrossVal_SuperNode.outputs)

    def execute(self, node_context):
        ms = sklearn.model_selection.TimeSeriesSplit(
            n_splits=node_context.parameters['n_splits'].value)
        self.use_model_select(node_context, ms)


class CrossVal_GroupKFold(CrossVal_GroupSuperNode):
    name = 'Group K-fold Cross Validation'
    icon = 'Kfold.svg'
    description = (
        'K-fold variant with non-overlapping groups.'
        'The same group will not appear in two different folds (the '
        'number of distinct groups has to be at least equal to the number '
        'of folds).')
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_groupkfold'

    parameters = node.parameters()
    parameters.set_integer('n_splits', value=3, label='Number of splits',
                           description='Number of folds, must be atleast 2')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        CrossVal_GroupSuperNode.inputs, CrossVal_GroupSuperNode.outputs)

    def execute(self, node_context):
        ms = sklearn.model_selection.GroupKFold(
            n_splits=node_context.parameters['n_splits'].value)
        self.use_model_select_group(node_context, ms)


class CrossVal_LeaveOneGroupOut(CrossVal_GroupSuperNode):
    name = 'Leave One Group out Cross Validation'
    icon = 'Kfold.svg'
    description = 'Gives splits for leave-one-group-out cross-validation'
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_leaveonegroupout'

    parameters = node.parameters()
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        CrossVal_GroupSuperNode.inputs, CrossVal_GroupSuperNode.outputs)

    def execute(self, node_context):
        ms = sklearn.model_selection.LeaveOneGroupOut()
        self.use_model_select_group(node_context, ms)


class CrossVal_evaluate(node.Node):
    name = 'Score Cross Validation'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.Partitioning)
    icon = 'cv_score.svg'
    description = (
        'Calculates the score for a model given a cross validation scheme')
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_score'

    inputs = Ports([
        ModelPort('in-model', name='in-model'),
        Port.Custom('[(table, table)]', 'splits', name='splits'),
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y'),
    ])
    outputs = Ports([Port.Table('scores', name='scores')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        out = node_context.output['scores']
        in_model = node_context.input['in-model']
        splits = node_context.input['splits']

        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)

        scores = []
        in_model.load()
        model = in_model.get_skl()
        splits_iter = (
            (split[0].get_column_to_array(split[0].column_names()[0]),
             split[1].get_column_to_array(split[1].column_names()[0]))
            for split in splits)
        scores = sklearn.model_selection.cross_val_score(
            model, X, Y, cv=splits_iter)
        N = len(scores)
        out.set_column_from_array("Scores", scores)
        out.set_column_from_array(
            "Mean", ma.array(np.r_[scores.mean(), np.zeros(N-1)],
                             mask=np.r_[0, np.ones(N-1)]))
        out.set_column_from_array(
            "Std", ma.array(np.r_[scores.std(), np.zeros(N-1)],
                            mask=np.r_[0, np.ones(N-1)]))


class CrossVal_split(node.Node):
    name = 'Split Data for Cross Validation'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.Partitioning)
    icon = 'cv_mux.svg'
    description = (
        'Partitions the data as per given training and test indicies. '
        'Returns list of tuples: (X training, Y training, X test, Y test)'
    )
    nodeid = 'org.sysess.sympathy.machinelearning.crossval_split'

    inputs = Ports([
        Port.Custom('[(table, table)]', 'splits', name='splits'),
        Port.Custom('table', 'data', name='data', n=(2, ))
    ])

    outputs = Ports([
        Port.Custom(
            tmpl.list(tmpl.tuple(tmpl.types(tmpl.group('data')),
                                 tmpl.types(tmpl.group('data')))),
            'out', name='out')
    ])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        data_tbls = node_context.input.group('data')
        splits = node_context.input['splits']
        out = node_context.output['out']

        data = [table_to_array(tbl) for tbl in data_tbls]
        default_names = (['X', 'Y', 'G'] +
                         ["D{}".format(i) for i in range(len(data))])

        for split in splits:
            train_idx = split[0].get_column_to_array(
                split[0].column_names()[0])
            test_idx = split[1].get_column_to_array(
                split[1].column_names()[0])
            tpl = out.create()

            for i in range(len(data)):
                tpl[i] = array_to_table(data_tbls[i].column_names(),
                                        data[i][train_idx])
                tpl[i].set_name((data_tbls[i].get_name()
                                 or default_names[i]) + " train")
            for i in range(len(data)):
                tpl[i+len(data)] = array_to_table(data_tbls[i].column_names(),
                                                  data[i][test_idx])
                tpl[i+len(data)].set_name((data_tbls[i].get_name()
                                           or default_names[i]) + " test")
            out.append(tpl)


class CrossVal_SimpleSplit(node.Node):
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.Partitioning)
    name = 'Simple Train-Test Split'
    icon = 'traintest.svg'
    description = (
        'Splits input data into a training and a test dataset'
    )
    nodeid = 'org.sysess.sympathy.machinelearning.simple_split'

    inputs = Ports([Port.Table('X', name='X'),
                    Port.Custom('table', 'Y', name='Y', n=(0, 1, 1))])
    outputs = Ports([
        Port.Table('X_train', name='X_train'),
        Port.Table('Y_train', name='Y_train'),
        Port.Table('X_test', name='X_test'),
        Port.Table('Y_test', name='Y_test'),
    ])

    parameters = node.parameters()
    parameters.set_float(
        'test_size', value=0.25,
        label='Test size',
        description='Size of test data as fraction (< 1) of all data')
    parameters.set_boolean('stratify', value=False, label='Stratify',
                           description='Stratify data using Y as class labels')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input.group('Y')
        if len(Y_tbl) > 0:
            Y_tbl = Y_tbl[0]
            Y = table_to_array(Y_tbl)
        else:
            Y_tbl = None
            Y = None
        X = table_to_array(X_tbl)

        if Y is None:
            X_train, X_test = (
                sklearn.model_selection.train_test_split(
                    X,
                    test_size=node_context.parameters['test_size'].value,
                ))
        else:
            if node_context.parameters['stratify'].value:
                stratify = Y[:, 0]
            else:
                stratify = None

            X_train, X_test, Y_train, Y_test = (
                sklearn.model_selection.train_test_split(
                    X, Y,
                    test_size=node_context.parameters['test_size'].value,
                    stratify=stratify
                ))

        X_train_tbl = node_context.output[0]
        Y_train_tbl = node_context.output[1]
        X_test_tbl = node_context.output[2]
        Y_test_tbl = node_context.output[3]

        array_to_table(X_tbl.column_names(), X_train, tbl=X_train_tbl)
        X_train_tbl.set_name((X_tbl.get_name() or "X") + " train")

        array_to_table(X_tbl.column_names(), X_test, tbl=X_test_tbl)
        X_test_tbl.set_name((X_tbl.get_name() or "X") + " test")

        if Y is not None:
            array_to_table(Y_tbl.column_names(), Y_train, tbl=Y_train_tbl)
            Y_train_tbl.set_name((Y_tbl.get_name() or "Y") + " train")

            array_to_table(Y_tbl.column_names(), Y_test, tbl=Y_test_tbl)
            Y_test_tbl.set_name((Y_tbl.get_name() or "Y") + " test")
