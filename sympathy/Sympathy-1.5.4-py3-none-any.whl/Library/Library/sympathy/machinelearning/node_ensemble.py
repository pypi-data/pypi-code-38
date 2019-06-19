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
import copy
import warnings

import sklearn
import sklearn.base
import sklearn.exceptions
import sklearn.multioutput
# Ignore a warning from numpy>=1.15.2 when importing sklearn.ensemble
# See issue #2768 for details.
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    import sklearn.ensemble

from sympathy.api import node
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags
from sympathy.api.exceptions import SyNodeError

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.ensemble import VotingClassifierDescriptor
from sylib.machinelearning.ensemble import MultiOutputClassifierDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract

from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import StringType


class VotingClassifier(SyML_abstract, node.Node):
    name = 'Voting Classifier'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'votingclassifier.svg'
    description = (
        'Uses voting to select answer from multiple classifiers. '
        'Add additional input ports for models by right-clicking on '
        'node and selecting "Create Input Port > models"')
    nodeid = 'org.sysess.sympathy.machinelearning.votingclassifier'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('models', 'models', n=(1,))])
    outputs = Ports([ModelPort('Output model', 'out-model')])

    descriptor = VotingClassifierDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'names',
         'type': StringType(default=''),
         'desc': 'Comma separated list of model names, eg. Rescale, SVC'},
        {'name': 'copies',
         'type': IntListType(default=[1]),
         'desc': 'Number of copies to make of each input model'},
        {'name': 'n_jobs',
         'type': IntType(default=1)},
        {'name': 'voting',
         'type': StringSelectionType(['hard', 'soft'])},
    ], doc_class=sklearn.ensemble.VotingClassifier)
    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'classes_',
        ]], doc_class=sklearn.ensemble.VotingClassifier)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        models = node_context.input.group('models')

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        names_raw = kwargs['names']
        copies = kwargs['copies']
        del kwargs['names']
        del kwargs['copies']

        name_list = [x.strip() for x in names_raw.split(',')]
        name_list = list(filter(lambda x: x != "", name_list))
        if len(name_list) < len(models):
            for i in range(len(name_list), len(models)):
                model = models[i]
                model.load()
                desc = model.get_desc()
                name_list.append(desc.name)
        else:
            name_list = name_list[:len(models)]

        descs = []
        skls = []
        names = []
        for i, model in enumerate(models):
            model.load()
            desc = model.get_desc()
            names.append(name_list[i])
            descs.append(model.get_desc())
            skls.append(model.get_skl())

        if len(copies) == 1 and copies[0] > 1:
            skls_ = []
            descs_ = []
            names_ = []
            for skl, desc, name in zip(skls, descs, names):
                skls_ += [copy.deepcopy(skl) for _ in range(copies[0])]
                descs_ += [copy.deepcopy(desc) for _ in range(copies[0])]
                names_ += ['{}-{}'.format(name, i+1) for i in range(copies[0])]
            skls = skls_
            descs = descs_
            names = names_

        elif len(copies) > 1:
            if len(copies) != len(skls):
                raise SyNodeError(
                    'Need to specify exactly one number as copies, or one '
                    'number for each of the {} different inputs'
                    .format(len(skls)))
            skls_ = []
            descs_ = []
            names_ = []
            for copies, skl, desc, name in zip(copies, skls, descs, names):
                skls_ += [copy.deepcopy(skl) for _ in range(copies)]
                descs_ += [copy.deepcopy(desc) for _ in range(copies)]
                names_ += ["{}-{}".format(name, i+1) for i in range(copies)]
            skls = skls_
            descs = descs_
            names = names_

        skl = sklearn.ensemble.VotingClassifier(
            list(zip(names, skls)), **kwargs)
        desc = self.__class__.descriptor.new(skl)

        out_model.set_skl(skl)
        out_model.set_desc(desc)
        desc.set_children(names, descs)
        out_model.save()


class MultiOutputClassifier(SyML_abstract, node.Node):
    name = 'Multi-output classifier'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'multioutput.svg'
    description = (
        'Fits one classifier for each target of outputs. Useful for '
        'extending classifiers that do not natively support multiple outputs')
    nodeid = 'org.sysess.sympathy.machinelearning.multioutput_classifier'
    tags = Tags(Tag.MachineLearning.Supervised)

    inputs = Ports([ModelPort('model', 'model', n=1)])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    descriptor = MultiOutputClassifierDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_jobs',
         'type': IntType(default=1)},
    ], doc_class=sklearn.multioutput.MultiOutputClassifier)
    descriptor.set_attributes([
    ], doc_class=sklearn.multioutput.MultiOutputClassifier)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        model = node_context.input['model']
        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)

        model.load()
        child_desc = model.get_desc()
        child_skl = model.get_skl()
        skl = sklearn.multioutput.MultiOutputClassifier(child_skl, **kwargs)
        desc = self.__class__.descriptor.new(skl)

        out_model.set_skl(skl)
        out_model.set_desc(desc)
        desc.set_child(child_desc)
        out_model.save()


class MultiOutputRegressor(SyML_abstract, node.Node):
    name = 'Multi-output regressor'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'multioutput.svg'
    description = (
        'Fits one regressor for each target of outputs. Useful for '
        'extending regressors that do not natively support multiple outputs')
    nodeid = 'org.sysess.sympathy.machinelearning.multioutput_regressor'
    tags = Tags(Tag.MachineLearning.Regression)

    inputs = Ports([ModelPort('model', 'model', n=1)])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    descriptor = MultiOutputClassifierDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_jobs',
         'type': IntType(default=1)},
    ], doc_class=sklearn.multioutput.MultiOutputRegressor)
    descriptor.set_attributes([
    ], doc_class=sklearn.multioutput.MultiOutputRegressor)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        model = node_context.input['model']
        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)

        model.load()
        child_desc = model.get_desc()
        child_skl = model.get_skl()
        skl = sklearn.multioutput.MultiOutputRegressor(child_skl, **kwargs)
        desc = self.__class__.descriptor.new(skl)

        out_model.set_skl(skl)
        out_model.set_desc(desc)
        desc.set_child(child_desc)
        out_model.save()
