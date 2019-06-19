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
import sklearn
import sklearn.base
import sklearn.exceptions
import sklearn.pipeline

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.pipeline import PipelineDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract


class Pipeline(node.Node):
    name = 'Pipeline'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'pipeline.svg'
    description = 'Applies one model on the output of another'
    nodeid = 'org.sysess.sympathy.machinelearning.pipeline'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('models', 'models', n=(2, ))])
    outputs = Ports([ModelPort('Output model', 'out-model')])

    descriptor = PipelineDescriptor()
    descriptor.name = name
    descriptor.set_info([])

    parameters = node.parameters()
    parameters.set_string(
        'names', value='', label='Model names',
        description=(
            'Comma separated list of model names, eg. Rescale, SVC. '
            'If fewer names are given than models then default names '
            'will be used.'))
    parameters.set_boolean(
        'flatten', value=True, label='Flatten',
        description=(
            'Flattens multiple pipeline objects into a single pipeline '
            'containing all models'))

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        models = node_context.input.group('models')
        names_raw = node_context.parameters['names'].value
        flatten = node_context.parameters['flatten'].value

        name_list = [x.strip() for x in names_raw.split(', ')]
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
            if flatten and isinstance(desc, PipelineDescriptor):
                names += [tpl[0] for tpl in desc.models]
                descs += [tpl[1] for tpl in desc.models]
                skls += [tpl[2] for tpl in desc.models]
            else:
                names.append(name_list[i])
                descs.append(model.get_desc())
                skls.append(model.get_skl())

        skl = sklearn.pipeline.Pipeline(list(zip(names, skls)))
        desc = self.__class__.descriptor.new(skl)
        out_model.set_desc(desc)
        out_model.set_skl(skl)
        desc.set_steps(names, descs)
        out_model.save()


class SplitPipeline(node.Node):
    name = 'Pipeline decomposition'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'pipeline_split.svg'
    description = 'Pick out given model from a fitted pipeline'
    nodeid = 'org.sysess.sympathy.machinelearning.pipeline_split'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('model', 'model')])
    outputs = Ports([ModelPort('Output model', 'out-model')])

    parameters = node.parameters()
    parameters.set_string(
        'name', value='A', label='Model name or index',
        description=(
            'Index (0 to N) or name of model to pick out from pipeline'))

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        model = node_context.input['model']
        name = node_context.parameters['name'].value

        model.load()
        desc = model.get_desc()

        out_desc = None, None
        try:
            index = int(name)
            _, out_desc, out_skl = list(desc.get_models())[index]
        except ValueError:
            for n, d, s in desc.get_models():
                if n == name:
                    out_desc, out_skl = d, s
                    break

        if out_desc is not None:
            out_model.set_desc(out_desc)
            out_model.set_skl(out_skl)
            out_model.save()
