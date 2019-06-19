# -*- coding: utf-8 -*-
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
"""
Some of the docstrings for this module have been automatically
extracted from the `scikit-learn <http://scikit-learn.org/>`_ library
and are covered by their respective licenses.
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import numpy as np

import sklearn
import sklearn.base
import sklearn.metrics
import sklearn.exceptions
import sklearn.model_selection
import sklearn.feature_selection

from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import sywarn

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringListType
from sylib.machinelearning.descriptors import StringType
from sylib.machinelearning.descriptors import UnionType

from sylib.machinelearning.utility import table_to_array


class ROCFromProb(SyML_abstract, node.Node):
    name = 'ROC from Probabilities'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'roc_curve.svg'
    description = (
        'Computes Receiver operating characteristics (ROC) based on '
        'calculated Y-probabilities and from true Y.')
    nodeid = 'org.sysess.sympathy.machinelearning.roc_prob'
    tags = Tags(Tag.MachineLearning.Metrics)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'pos_label',
         'type': UnionType([
             NoneType(), IntType(), StringType()], default=None)},
        {'name': 'drop_intermediate',
         'type': BoolType(default=True)},
        {'name': 'header as label',
         'desc': 'Use header of Y-prob as the target label',
         'no-kw': True,
         'type': BoolType(default=True)},
    ], doc_class=sklearn.metrics.roc_curve)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([Port.Table('Y-prob', name='Y-prob'),
                    Port.Table('Y-true', name='Y-true')])
    outputs = Ports([Port.Table('roc', name='roc')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        Y_prob_tbl = node_context.input['Y-prob']
        Y_true_tbl = node_context.input['Y-true']
        roc_tbl = node_context.output['roc']
        header_as_label = node_context.parameters['header as label'].value

        Y_prob = table_to_array(Y_prob_tbl)
        Y_true = table_to_array(Y_true_tbl)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        kwargs['y_true'] = Y_true
        kwargs['y_score'] = Y_prob
        if BoolType().from_string(header_as_label):
            label = Y_prob_tbl.column_names()[0]
            try:
                label = int(label)
            except ValueError:
                pass
            kwargs['pos_label'] = label
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(**kwargs)
        roc_tbl.set_column_from_array('false positive rate', fpr)
        roc_tbl.set_column_from_array('true positive rate', tpr)
        roc_tbl.set_column_from_array('threshold', thresholds)
        roc_tbl.set_name('ROC')


class R2Score(SyML_abstract, node.Node):
    name = 'R² regression score (R2)'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'roc_curve.svg'
    description = (
        'Computes the R² regression score.\n'
        'Best possible score is 1.0 and it can be negative (because the model '
        'can be arbitrarily bad). A constant model that always predicts the '
        'expected value of y, disregarding the input features, would get a '
        'R² score of 0.0) ')
    nodeid = 'org.sysess.sympathy.machinelearning.r2_score'
    tags = Tags(Tag.MachineLearning.Metrics)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
    ], doc_class=sklearn.metrics.r2_score)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([Port.Table('Y-prob', name='Y-prob'),
                    Port.Table('Y-true', name='Y-true')])
    outputs = Ports([Port.Table('r2 score', name='r2 score')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        Y_prob_tbl = node_context.input['Y-prob']
        Y_true_tbl = node_context.input['Y-true']
        r2_tbl = node_context.output['r2 score']

        Y_prob = table_to_array(Y_prob_tbl)
        Y_true = table_to_array(Y_true_tbl)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        kwargs['y_true'] = Y_true
        kwargs['y_pred'] = Y_prob

        r2_score = sklearn.metrics.r2_score(**kwargs)
        if isinstance(r2_score, np.ndarray):
            r2_tbl.set_column_from_array('r² score', r2_score)
        else:
            r2_tbl.set_column_from_array('r² score', np.array([r2_score]))

        r2_tbl.set_name('R² score')


class ConfusionFromPrediction(SyML_abstract, node.Node):
    name = 'Confusion Matrix'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'confusion_matrix.svg'
    description = (
        'Computes the confusion matrix given predictions and true Y-values.')
    nodeid = 'org.sysess.sympathy.machinelearning.confusion'
    tags = Tags(Tag.MachineLearning.Metrics)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'labels',
         'type': UnionType([
             NoneType(), IntListType(), StringListType()], default="")},
        {'name': 'include heading',
         'desc': 'Adds a columns with used class names',
         'no-kw': True,
         'type': BoolType(default=True)},
    ], doc_class=sklearn.metrics.confusion_matrix)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([Port.Table('Y-pred', name='Y-pred'),
                    Port.Table('Y-true', name='Y-true')])
    outputs = Ports([Port.Table('confusion-matrix', name='confusion-matrix')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        Y_pred_tbl = node_context.input['Y-pred']
        Y_true_tbl = node_context.input['Y-true']
        cm_tbl = node_context.output['confusion-matrix']
        heading = BoolType().from_string(
            node_context.parameters['include heading'].value)

        Y_pred = table_to_array(Y_pred_tbl)
        Y_true = table_to_array(Y_true_tbl)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        kwargs['y_true'] = Y_true
        kwargs['y_pred'] = Y_pred
        if kwargs['labels'] == []:
            kwargs['labels'] = None
        cm = sklearn.metrics.confusion_matrix(**kwargs)
        if kwargs['labels'] is not None:
            cols = kwargs['labels']
        else:
            cols = sorted(list(set(Y_true.ravel())))

        if heading:
            cm_tbl.set_column_from_array('label', np.array(cols))
        for i, col in enumerate(cols):
            cm_tbl.set_column_from_array(str(cols[i]), cm[:, i])
        if Y_true_tbl.get_name() is None:
            cm_tbl.set_name("Confusion matrix")
        else:
            cm_tbl.set_name(Y_true_tbl.get_name()+" confusion matrix")


class LearningCurve(node.Node):
    name = 'Learning Curve'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'learning_curve.svg'
    description = (
        'Generates a learning curve by training model multiple times'
        'on incrementally larger subsets of the data and using '
        'cross validation for scoring. '
        'Plot performance of train-mean vs. test-mean for curve.')
    nodeid = 'org.sysess.sympathy.machinelearning.learningcurve'
    tags = Tags(Tag.MachineLearning.Metrics)

    parameters = node.parameters()
    parameters.set_boolean(
        'shuffle', value=True, label='Shuffle',
        description='Randomizes the input dataset before passed to '
        'internal cross validation')
    parameters.set_float(
        'smallest', value=0.1, label='Smallest fraction',
        description='Size of the smallest dataset as fraction of total')
    parameters.set_integer(
        'steps', value=10, label='Steps',
        description='Number of different sizes of training/test data measured')
    parameters.set_integer(
        'cv', value=3, label='Cross validation folds',
        description='Number of fold of cross-validation (minimum 2)')

    inputs = Ports([
        ModelPort('Model', 'model'),
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y')
    ])
    outputs = Ports([
        Port.Table('results', name='results'),
        Port.Table('statistics', name='statistics')
    ])

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        results = node_context.output['results']
        statistics = node_context.output['statistics']
        shuffle = node_context.parameters['shuffle'].value
        smallest = node_context.parameters['smallest'].value
        steps = node_context.parameters['steps'].value
        cv = node_context.parameters['cv'].value

        smallest = max(0, min(smallest, 1.0))
        cv = max(2, cv)

        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)

        if shuffle:
            perm = np.random.permutation(X.shape[0])
            X = X[perm]
            Y = Y[perm]

        in_model = node_context.input['model']
        in_model.load()
        skl = in_model.get_skl()

        sizes, train_scores, test_scores = (
            sklearn.model_selection.learning_curve(
                skl, X, Y[:, 0], cv=cv,
                train_sizes=np.linspace(smallest, 1.0, steps)))

        N = train_scores.shape[1]
        sizes_all = np.repeat(sizes, N)
        results.set_column_from_array("sizes", sizes_all)
        results.set_column_from_array("train", train_scores.ravel())
        results.set_column_from_array("test", test_scores.ravel())

        statistics.set_column_from_array("sizes", sizes)
        statistics.set_column_from_array("train_mean",
                                         np.mean(train_scores, axis=1))
        statistics.set_column_from_array("test_mean",
                                         np.mean(test_scores, axis=1))
        statistics.set_column_from_array("train_median",
                                         np.median(train_scores, axis=1))
        statistics.set_column_from_array("test_median",
                                         np.median(test_scores, axis=1))


class ConditionalFromCategories(node.Node):
    name = 'Conditional Probabilty from Categories'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'cond_prob_cat.svg'
    description = (
        'Creates groups of all (categorical) features and gives probabilities'
        'for Y. All of X must be categorical and all Y binary')
    nodeid = 'org.sysess.sympathy.machinelearning.cond_prob_cat'
    tags = Tags(Tag.MachineLearning.Metrics)

    parameters = node.parameters()
    inputs = Ports([
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y')
    ])
    outputs = Ports([
        Port.Table('results', name='results'),
    ])

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        results = node_context.output['results']

        X_names = X_tbl.column_names()
        Y_names = Y_tbl.column_names()

        dfX = X_tbl.to_dataframe()

        dfXY = dfX.copy()
        for col_y in Y_names:
            if col_y in X_names:
                sywarn('Column {} exists in both X, Y'.format(col_y))
            else:
                dfXY.loc[:, col_y] = Y_tbl.get_column_to_series(col_y)

        means = dfXY.groupby(X_names).mean()
        xy_indices = np.array(list(means.index))
        y_means = np.array(means)
        if len(xy_indices.shape) == 1:
            xy_indices = xy_indices.reshape(xy_indices.shape+(1,))
        if len(y_means.shape) == 1:
            y_means = y_means.reshape(y_means.shape+(1,))

        for i, col_x in enumerate(X_names):
            results.set_column_from_array(col_x, xy_indices[:, i])
        for i, col_y in enumerate(Y_names):
            results.set_column_from_array(col_y, y_means[:, i])
