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
import sklearn.cluster

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class KMeansClustering(SyML_abstract, node.Node):
    name = 'K-means Clustering'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Clusters data by trying to separate samples in n groups of equal '
        'variance')
    nodeid = 'org.sysess.sympathy.machinelearning.k_means'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_clusters',
         'type': IntType(default=8)},
        {'name': 'max_iter',
         'type': IntType(default=300)},
        {'name': 'n_init',
         'type': IntType(default=10)},
        {'name': 'init',
         'type': StringSelectionType(
             ['k-means++', 'random'], default='k-means++')},
        {'name': 'algorithm',
         'type': StringSelectionType(
             ['auto', 'full', 'elkan'], default='auto')},
        {'name': 'precompute_distances',
         'type': UnionType([
             StringSelectionType(['auto']), BoolType()], default='auto')},
        {'name': 'tol',
         'type': FloatType(min_value=0, default=1e-4)},
        {'name': 'n_jobs',
         'type': IntType(min_value=1)},
        {'name': 'random_state',
         'type': UnionType([NoneType(), IntType()], default=None)},
    ], doc_class=sklearn.cluster.KMeans)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'cluster_centers_', 'labels_', 'inertia_'
        ]], doc_class=sklearn.cluster.KMeans)

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
        skl = sklearn.cluster.KMeans(**kwargs)

        model.set_skl(skl)
        model.save()


class MiniBatchKMeansClustering(SyML_abstract, node.Node):
    name = 'Mini-batch K-means Clustering'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Variant of the KMeans algorithm which uses mini-batches to reduce the'
        ' computation time')
    nodeid = 'org.sysess.sympathy.machinelearning.mini_batch_k_means'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_clusters',
         'type': IntType(default=8)},
        {'name': 'max_iter',
         'type': IntType(default=300)},
        {'name': 'max_no_improvement',
         'type': UnionType([IntType(), NoneType()], default=10)},
        {'name': 'batch_size',
         'type': IntType(default=100, min_value=1)},
        {'name': 'init_size',
         'type': IntType(default=300, min_value=1)},
        {'name': 'n_init',
         'type': IntType(default=3)},
        {'name': 'init',
         'type': StringSelectionType(
             ['k-means++', 'random'], default='k-means++')},
        {'name': 'compute_labels',
         'type': BoolType(default=True)},
        {'name': 'reassignment_ratio',
         'type': FloatType(default=0.01)},
        {'name': 'tol',
         'type': FloatType(min_value=0, default=1e-4)},
        {'name': 'random_state',
         'type': UnionType([NoneType(), IntType()], default=None)},
    ], doc_class=sklearn.cluster.MiniBatchKMeans)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'cluster_centers_', 'labels_', 'inertia_'
        ]], doc_class=sklearn.cluster.MiniBatchKMeans)

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
        skl = sklearn.cluster.MiniBatchKMeans(**kwargs)

        model.set_skl(skl)
        model.save()
