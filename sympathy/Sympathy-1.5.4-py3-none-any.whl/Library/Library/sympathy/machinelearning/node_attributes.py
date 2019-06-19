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

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from sympathy.api import node
from sympathy.api import ParameterView
from sympathy.api.nodeconfig import Port
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags
from sympathy.api.exceptions import SyNodeError

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import coerce_to_np
from sylib.machinelearning.utility import value_to_tables


class AttributeParameterWidget(ParameterView):
    def __init__(self, node_context, parent=None):
        super(ParameterView, self).__init__(parent=parent)
        self._parameters = node_context.parameters
        self._validator = None

        in_model = node_context.input['in-model']
        in_model.load()
        desc = in_model.get_desc()

        self.attrs = desc.attributes
        self.attr_sel = QtGui.QComboBox()
        self.doc_label = QtGui.QLabel("")

        for pos, attr in enumerate(self.attrs):
            self.attr_sel.addItem(attr['name'])
            self.attr_sel.setItemData(pos, attr['desc'], QtCore.Qt.ToolTipRole)

        if len(self.attrs) > 0:
            # Set initially used attribute
            index = self.attr_sel.findText(self._parameters['attribute'].value,
                                           QtCore.Qt.MatchFixedString)
            if index < 0:
                index = 0
            self.attr_sel.setCurrentIndex(index)
            self.attr = self.attrs[index]
            self.attr_sel.currentIndexChanged.connect(self.attribute_selected)

            self.attr_sel.setToolTip(self.attrs[index]['desc'])
            self.doc_label.setText(self.attrs[index]['desc'])
            self.attribute_selected(index)

        # Add to layout
        self.options_layout = QtGui.QVBoxLayout()
        self.options_layout.addWidget(self.attr_sel)
        self.options_layout.addWidget(self.doc_label)
        self.options_layout.addStretch(1)
        self.setLayout(self.options_layout)

    def attribute_selected(self, index):
        self.attr = self.attrs[index]
        self._parameters['attribute'].value = self.attrs[index]['name']
        self.attr_sel.setToolTip(self.attrs[index]['desc'])
        self.doc_label.setText(self.attrs[index]['desc'])


class ExtractAttribute(node.Node):
    name = 'Extract Attributes'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'attributes.svg'
    description = (
        'Extract attributes from a fitted model, requires model dependent '
        'name for the attribute')
    nodeid = 'org.sysess.sympathy.machinelearning.extract_attributes'
    tags = Tags(Tag.MachineLearning.Apply)

    parameters = node.parameters()
    parameters.set_string(
        'attribute', value="", label='attribute',
        description='Name of attribute to extract')
    inputs = Ports([ModelPort('Input model', 'in-model')])
    outputs = Ports([Port.Tables('Attributes', name='out')])

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        attr_name = node_context.parameters['attribute'].value
        if attr_name == '':
            raise SyNodeError('No attribute selected yet')
        in_model = node_context.input['in-model']
        in_model.load()
        skl = in_model.get_skl()
        desc = in_model.get_desc()

        try:
            value = desc.get_attribute(skl, attr_name)
        except AttributeError:
            raise SyNodeError('No attribute {} in object'.format(attr_name))

        value = coerce_to_np(value)
        out = node_context.output['out']

        cnames = None
        rnames = None
        for attr_dict in desc.attributes:
            if attr_dict['name'] == attr_name:
                if 'cnames' in attr_dict:
                    cnames = attr_dict['cnames'](desc, skl)
                if 'rnames' in attr_dict:
                    rnames = attr_dict['rnames'](desc, skl)
                break

        tbls = value_to_tables(value, attr_name, cnames=cnames, rnames=rnames)
        for tbl in tbls:
            out.append(tbl)

    def exec_parameter_view(self, node_context):
        if node_context.input['in-model'].is_valid():
            return AttributeParameterWidget(node_context)
        else:
            return QtGui.QLabel(
                'Node must have a model as input before it can be configured')
