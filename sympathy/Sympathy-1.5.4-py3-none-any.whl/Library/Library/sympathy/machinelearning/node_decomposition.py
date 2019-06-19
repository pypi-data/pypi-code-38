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
import sklearn.decomposition
import sklearn.cross_decomposition

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags
from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y
from sylib.machinelearning.utility import names_from_prefix
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class PrincipalComponentAnalysis(SyML_abstract, node.Node):
    name = 'Principal Component Analysis (PCA)'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Linear dimensionality reduction using Singular Value Decomposition '
        'of the data to project it to a lower dimensional space.')
    nodeid = 'org.sysess.sympathy.machinelearning.pca'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_components',
         'type': UnionType(
             [IntType(min_value=1), FloatType(min_value=0, max_value=1),
              StringSelectionType(['mle'])], default=1)},
        {'name': 'svd_solver',
         'type': StringSelectionType(
             ['auto', 'full', 'arpack', 'randomized'], default='auto')},
        {'name': 'tol',
         'type': FloatType(default=0.0)},
        {'name': 'iterated_power',
         'type': UnionType(
             [IntType(min_value=0), StringSelectionType(['auto'])],
             default='auto')},
        {'name': 'whiten',
         'type': BoolType(default=False)},
    ], doc_class=sklearn.decomposition.PCA)

    descriptor.set_attributes([
        {'name': 'components_', 'cnames': names_from_x},
        {'name': 'explained_variance_'},
        {'name': 'explained_variance_ratio_'},
        {'name': 'mean_', 'cnames': names_from_x},
        {'name': 'n_components_'},
        {'name': 'noise_variance_'},
    ], doc_class=sklearn.decomposition.PCA)

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
        skl = sklearn.decomposition.PCA(**kwargs)

        model.set_skl(skl)
        model.save()


class KernelPCA(SyML_abstract, node.Node):
    name = 'Kernel Principal Component Analysis (KPCA)'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Non-linear dimensionality reduction through the use of kernels')
    nodeid = 'org.sysess.sympathy.machinelearning.kpca'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_components',
         'type': UnionType(
             [IntType(min_value=1), NoneType()], default=None)},
        {'name': 'kernel',
         'type': StringSelectionType(
             ['linear', 'poly', 'rbf', 'sigmoid', 'cosine', 'precomputed'],
             default='linear')},
        {'name': 'degree',
         'type': IntType(min_value=1, default=3)},
        {'name': 'gamma',
         'type': UnionType([
             FloatType(min_value=0.0), NoneType()], default=None)},
        {'name': 'coef0',
         'type': FloatType(min_value=0.0, default=1)},
        {'name': 'alpha',
         'type': IntType(min_value=0.0, default=1)},
        {'name': 'fit_inverse_transform',
         'type': BoolType(default=False)},
        {'name': 'remove_zero_eig',
         'type': BoolType(default=False)},
        {'name': 'eigen_solver',
         'type': StringSelectionType([
             'auto', 'dense', 'arpack'], default='auto')},
        {'name': 'tol',
         'type': FloatType(default=0.0)},
        {'name': 'max_iter',
         'type': UnionType([IntType(min_value=1), NoneType()], default=None)},
        {'name': 'random_state',
         'type': UnionType([NoneType(), IntType()], default=None)},
        {'name': 'n_jobs',
         'type': IntType(min_value=1)},
    ], doc_class=sklearn.decomposition.KernelPCA)

    descriptor.set_attributes([
        {'name': 'lambdas_'},
        {'name': 'alphas_'},
        {'name': 'dual_coef_', 'cnames': names_from_x},
        {'name': 'X_transformed_fit_'},
        {'name': 'X_fit_'},
    ], doc_class=sklearn.decomposition.KernelPCA)

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
        kwargs['copy_X'] = True
        skl = sklearn.decomposition.KernelPCA(**kwargs)

        model.set_skl(skl)
        model.save()


class PLSRegressionCrossDecomposition(SyML_abstract, node.Node):
    name = 'Partial Least Squares cross-decomposition (PLS regression)'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Finds the fundamental relations between two matrices X and Y, ie. '
        'it finds the (multidimensional) direction in X that best explains '
        'maximum multidimensional direction in Y. See also PCA-analysis')
    nodeid = 'org.sysess.sympathy.machinelearning.pls'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_components',
         'type': IntType(min_value=1, default=2)},
        {'name': 'scale',
         'type': BoolType(default=True)},
        {'name': 'max_iter',
         'type': IntType(min_value=1, default=500)},
        {'name': 'tol',
         'type': FloatType(default=0.0)},
    ], doc_class=sklearn.cross_decomposition.PLSRegression)

    descriptor.set_attributes([
        {'name': 'x_weights_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_weights_',
         'rnames': names_from_y,
         'cnames': names_from_prefix('component ')},
        {'name': 'x_loadings_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_loadings_',
         'rnames': names_from_y,
         'cnames': names_from_prefix('component ')},
        {'name': 'x_scores_',
         'cnames': names_from_prefix('component ')},
        {'name': 'y_scores_',
         'cnames': names_from_prefix('component ')},
        {'name': 'x_rotations_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_rotations_',
         'rnames': names_from_y},
        {'name': 'coef_'},
        {'name': 'n_iter_'},
    ], doc_class=sklearn.cross_decomposition.PLSRegression)

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
        skl = sklearn.cross_decomposition.PLSRegression(**kwargs)

        model.set_skl(skl)
        model.save()
