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
import sklearn.linear_model
import sklearn.kernel_ridge

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class LinearRegression(SyML_abstract, node.Node):
    name = 'Linear Regression'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'linear_regression.svg'
    description = 'Ordinary linear regression'
    nodeid = 'org.sysess.sympathy.machinelearning.linearregression'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'fit_intercept',
         'type': BoolType(default=True)},
        {'name': 'normalize',
         'type': BoolType(default=False)},
        {'name': 'n_jobs',
         'type': IntType(min_value=1, default=1)},
    ], doc_class=sklearn.linear_model.LinearRegression)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'coef_', 'intercept_', 'residues_',
        ]], doc_class=sklearn.linear_model.LinearRegression)

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
        skl = sklearn.linear_model.LinearRegression(**kwargs)

        model.set_skl(skl)
        model.save()


class LogisticRegression(SyML_abstract, node.Node):
    name = 'Logistic Regression'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'logistic_regression.svg'
    description = 'Logistic regression of a categorical dependent variable'
    nodeid = 'org.sysess.sympathy.machinelearning.logisticregression'
    tags = Tags(Tag.MachineLearning.Supervised)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        ['Options',
         {'name': 'penalty',
          'type': StringSelectionType(['l1', 'l2'], default='l2')},
         {'name': 'dual',
          'type': BoolType(default=False)},
         {'name': 'C',
          'type': FloatType(min_value=0, default=1.0)},
         {'name': 'fit_intercept',
          'type': BoolType(default=True)},
         {'name': 'intercept_scaling',
          'type': FloatType(default=1.0)},
         {'name': 'class_weight',
          'type': UnionType([
              NoneType(), StringSelectionType(['balanced'])], default=None)},
         {'name': 'tol',
          'type': FloatType(default=1e-4)},
         {'name': 'multi_class',
          'type': StringSelectionType(['ovr', 'multinomial'], default='ovr')}],
        ['Solver',
         {'name': 'max_iter',
          'type': IntType(min_value=0, default=100)},
         {'name': 'solver',
          'type': StringSelectionType(
              ['newton-cg', 'lbfgs', 'liblinear', 'sag'],
              default='liblinear')},
         {'name': 'n_jobs',
          'desc': (
              'Number of CPU cores used when parallelizing over classes if '
              'multi_class="ovr". Ignored when the solver is set to '
              '"liblinear" regardless of multi_class. If given -1 then all '
              'cores are used'),
          'type': IntType(min_value=1, default=1)}],
        ['Model state',
         {'name': 'random_state',
          'type': UnionType([NoneType(), IntType()], default=None)},
         {'name': 'warm_start', 'type': BoolType(default=False)}],
    ], doc_class=sklearn.linear_model.LogisticRegression)

    descriptor.set_attributes([
        {'name': 'n_iter_'},
        {'name': 'coef_', 'cnames': names_from_x},
        {'name': 'intercept_'},
    ], doc_class=sklearn.linear_model.LogisticRegression)

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
        skl = sklearn.linear_model.LogisticRegression(**kwargs)

        model.set_skl(skl)
        model.save()


class KernelRidge(SyML_abstract, node.Node):
    name = 'Kernel Ridge Regression'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'kernel_ridge.svg'
    description = (
        'Kernel Ridge based classifier combining ridge regression '
        '(linear least-squares L2-norm) regression with the kernel trick')
    nodeid = 'org.sysess.sympathy.machinelearning.kernel_ridge'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'alpha',
         'type': FloatType(min_value=0, default=1.0)},
        {'name': 'kernel',
         'type': StringSelectionType(
             ['linear', 'rbf', 'poly', 'sigmoid', 'cosine',
              'laplacian', 'chi2'], default='rbf')},
        {'name': 'gamma',
         'type': UnionType([NoneType(), FloatType()], default=None)},
        {'name': 'coef0',
         'type': FloatType(default=1.0)},
        {'name': 'degree',
         'type': IntType(min_value=1, default=3)},
         ], doc_class=sklearn.kernel_ridge.KernelRidge)

    descriptor.set_attributes([
        {'name': 'dual_coef_', 'cnames': names_from_y},
        {'name': 'X_fit_', 'cnames': names_from_x},
    ], doc_class=sklearn.kernel_ridge.KernelRidge)

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
        skl = sklearn.kernel_ridge.KernelRidge(**kwargs)

        model.set_skl(skl)
        model.save()


class SupportVectorRegression(SyML_abstract, node.Node):
    name = 'Epsilon Support Vector Regression'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'svm.svg'
    description = 'Support vector machine based regressor (SVR)'
    nodeid = 'org.sysess.sympathy.machinelearning.svr'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'C',
         'type': FloatType(default=1.0)},
        {'name': 'kernel',
         'type': StringSelectionType(
             ['linear', 'rbf', 'poly', 'sigmoid'], default='rbf')},
        {'name': 'gamma',
         'type': UnionType([
             StringSelectionType(['auto']), FloatType()], default='auto')},
        {'name': 'epsilon',
         'type': FloatType(default=0.1)},
        {'name': 'coef0',
         'type': FloatType(default=0.0)},
        {'name': 'tol',
         'type': FloatType(default=1e-3)},
        {'name': 'degree',
         'type': IntType(min_value=1, default=3)},
        {'name': 'shrinking',
         'type': BoolType(default=True)},
        {'name': 'max_iter',
         'type': IntType(default=-1)},
    ], doc_class=sklearn.svm.SVR)

    descriptor.set_attributes([
        {'name': 'support_', },
        {'name': 'support_vectors_', 'cnames': names_from_x},
        {'name': 'dual_coef_'},
        {'name': 'intercept_'},
        {'name': 'coef_', 'cnames': names_from_x},
    ], doc_class=sklearn.svm.SVR)

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
        skl = sklearn.svm.SVR(**kwargs)

        model.set_skl(skl)
        model.save()
