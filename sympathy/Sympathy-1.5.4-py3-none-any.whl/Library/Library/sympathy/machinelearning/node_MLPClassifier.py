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
import sklearn
import sklearn.neural_network

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.neuralnetwork import MLPClassifierDescriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class MLPClassifier(SyML_abstract, node.Node):
    name = 'Multi-Layer Perceptron Classifier'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'neuralnetwork.svg'
    description = 'Multi-layer perceptron classifier'
    nodeid = 'org.sysess.sympathy.machinelearning.mlp__classifier'
    tags = Tags(Tag.MachineLearning.Supervised)

    descriptor = MLPClassifierDescriptor()
    descriptor.name = name
    descriptor.set_info([
        [
            "Architecture",
            {'name': 'max_iter', 'type': IntType(default=200, min_value=0)},
            {'name': 'hidden_layer_sizes',
             'type': IntListType(default=[100], min_value=1)},
            {'name': 'activation',
             'type': StringSelectionType([
                 'identity', 'logistic', 'tanh', 'relu'], default='relu')},
        ],
        [
            "Solving methods",
            {'name': 'solver',
             'type': StringSelectionType([
                 'lbfgs', 'sgd', 'adam'], default='adam')},
            {'name': 'batch_size',
             'type': UnionType([
                 IntType(min_value=1),
                 StringSelectionType(['auto'])
             ], default='auto')},
            {'name': 'learning_rate',
             'type': StringSelectionType([
                 'constant', 'invscaling', 'adaptive'
             ])},
            {'name': 'shuffle',
             'type': BoolType(default=True)},
            {'name': 'early_stopping',
             'type': BoolType(default=False)},
            {'name': 'validation_fraction',
             'type': FloatType(default=0.1, min_value=0.0, max_value=1.0)},
        ],
        [
            "Solver parameters",
            {'name': 'alpha',
             'type': FloatType(default=1e-5, min_value=0.0)},
            {'name': 'tol', 'type': FloatType(default=1e-4, min_value=0.0)},
            {'name': 'learning_rate_init',
             'type': FloatType(default=1e-3, min_value=0.0)},
            {'name': 'power_t', 'type': FloatType(default=0.5, min_value=0.0)},
            {'name': 'momentum',
             'type': FloatType(default=0.9, min_value=0.0, max_value=1.0)},
            {'name': 'nesterovs_momentum',
             'type': BoolType(default=True)},
            {'name': 'beta_1',
             'type': FloatType(default=0.9, min_value=0.0, max_value=1.0)},
            {'name': 'beta_2',
             'type': FloatType(default=0.999, min_value=0.0, max_value=1.0)},
            {'name': 'epsilon',
             'type': FloatType(default=1e-8, min_value=0.0)},
        ],
        [
            "Model state",
            {'name': 'random_state',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'warm_start', 'type': BoolType(default=False)},
        ]
    ], doc_class=sklearn.neural_network.MLPClassifier)
    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'classes_', 'loss_', 'coefs_', 'intercepts_', 'n_iter_',
            'n_layers_', 'n_outputs_', 'out_activation_',
        ]], doc_class=sklearn.neural_network.MLPClassifier)

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
        skl = sklearn.neural_network.MLPClassifier(**kwargs)

        model.set_skl(skl)
        model.save()
