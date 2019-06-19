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
import inspect
import warnings

import sklearn
# Ignore a warning from numpy>=1.15.2 when importing sklearn.ensemble
# See issue #2768 for details.
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    import sklearn.ensemble

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.decisiontrees import RandomForestDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class RandomForestClassifier(SyML_abstract, node.Node):
    name = 'Random Forest Classifier'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'forest.svg'
    description = (
        'A random forest is a meta estimator that fits a number of decision '
        'tree classifiers on various sub-samples of the dataset and use '
        'averaging to improve the predictive accuracy and control '
        'over-fitting. The sub-sample size is always the same as the original '
        'input sample size but the samples are drawn with replacement if '
        'bootstrap is True (default).')
    nodeid = 'org.sysess.sympathy.machinelearning.random_forest_classifier'
    tags = Tags(Tag.MachineLearning.Supervised)

    # Test for existance of 'impurity_decrease' parameter (scikit-learn 0.19+)
    param_impurity_decrease = (
        'min_impurity_decrease' in inspect.getargspec(
            sklearn.ensemble.RandomForestClassifier.__init__)[0]
    )

    descriptor = RandomForestDescriptor()
    descriptor.name = name
    info = [
        [
            "Basic",
            {'name': 'n_estimators',
             'type': IntType(min_value=1, default=3)},
            {'name': 'criterion',
             'type': StringSelectionType(['gini', 'entropy'])},
            {'name': 'bootstrap',
             'type': BoolType(default=True)},
            {'name': 'oob_score',
             'type': BoolType(default=True)},
            {'name': 'n_jobs',
             'type': IntType(min_value=-1, default=-1)},
        ],
        [
            "Node growth",
            {'name': 'max_features',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0),
                 StringSelectionType([
                     'auto', 'sqrt', 'log2']),
                 NoneType()], default="None")},
            {'name': 'max_depth',
             'type': UnionType([IntType(min_value=1), NoneType()])},
            {'name': 'min_samples_split',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)
             ], default="2")},
            {'name': 'min_samples_leaf',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)
             ], default="1")},
            {'name': 'min_samples_leaf',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)
             ], default="1")},
            {'name': 'min_weight_fraction_leaf',
             'type': FloatType(min_value=0.0, default=0.0)},
            {'name': 'max_leaf_nodes',
             'type': UnionType([IntType(min_value=0),
                                NoneType()], default="None")},
            {'name': 'min_impurity_split',
             'type': FloatType(min_value=0.0, default=1e-7),
             'deprecated': param_impurity_decrease},
        ],
        [
            "Model state",
            {'name': 'random_state',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'warm_start', 'type': BoolType(default=False)},
        ],
    ]
    if param_impurity_decrease:
        info[1].append({'name': 'min_impurity_decrease',
                        'type': FloatType(default=0)})
    descriptor.set_info(info,
                        doc_class=sklearn.ensemble.RandomForestClassifier)

    descriptor.set_attributes([
        {'name': 'classes_'},
        {'name': 'feature_importances_', 'cnames': names_from_x},
        {'name': 'n_classes_'},
        {'name': 'n_features_'},
        {'name': 'n_outputs_'},
        {'name': 'oob_score_'},
        {'name': 'oob_decision_function_'},
    ], doc_class=sklearn.ensemble.RandomForestClassifier)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([])
    outputs = Ports([ModelPort('Model', 'model')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        model = node_context.output['model']
        desc = self.__class__.descriptor
        model.set_desc(desc)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        skl = sklearn.ensemble.RandomForestClassifier(**kwargs)

        model.set_skl(skl)
        model.save()
