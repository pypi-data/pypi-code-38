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
import sklearn.feature_extraction

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.count_vectorizer import CountVectorizerDescriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringListType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import StringType
from sylib.machinelearning.descriptors import UnionType


class CountVectorizer(SyML_abstract, node.Node):
    name = 'Text Count Vectorizer'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'count_vectorizer.svg'
    description = (
        'Convert a collection of text documents to a matrix of token counts')
    nodeid = 'org.sysess.sympathy.machinelearning.count_vectorizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = CountVectorizerDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'encoding',
         'type': StringType(default='utf-8')},
        {'name': 'decode_error',
         'type': StringSelectionType(['strict', 'ignore', 'replace'],
                                     default='strict')},
        {'name': 'strip_accents',
         'type': UnionType([StringSelectionType(['ascii', 'unicode']),
                            NoneType()], default=None)},
        {'name': 'analyzer',
         'type': StringSelectionType(['word', 'char', 'char_wb'],
                                     default='word')},
        {'name': 'ngram_range',
         'type': IntListType(min_value=1, min_length=2, max_length=2,
                             default=[1, 3])},
        {'name': 'stop_words',
         'type': UnionType([StringSelectionType('english'),
                            StringListType(min_length=1),
                            NoneType()], default='english')},
        {'name': 'lowercase',
         'type': BoolType(default=True)},
        # {'name': 'token_pattern',
        #  'type': UnionType([StringType(), NoneType()], default=None)},
        {'name': 'max_df',
         'type': UnionType([
             IntType(min_value=0),
             FloatType(min_value=0.0, max_value=1.0)], default=1.0)},
        {'name': 'min_df',
         'type': UnionType([
             IntType(min_value=0),
             FloatType(min_value=0.0, max_value=1.0)], default=0.0)},
        {'name': 'max_features',
         'type': UnionType([IntType(min_value=1),
                            NoneType()], default=None)},
        {'name': 'binary',
         'type': BoolType(default=False)},
    ], doc_class=sklearn.feature_extraction.text.CountVectorizer)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'vocabulary_', 'stop_words_'
        ]], doc_class=sklearn.feature_extraction.text.CountVectorizer)

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
        skl = sklearn.feature_extraction.text.CountVectorizer(**kwargs)

        model.set_skl(skl)
        model.save()
