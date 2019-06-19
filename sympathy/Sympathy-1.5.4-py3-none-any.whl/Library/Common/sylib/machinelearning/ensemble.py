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
from PySide import QtGui
from PySide.QtCore import Qt

import copy
import six

from sylib.machinelearning.descriptors import Descriptor
from sylib.machinelearning.model import set_model_tooltip

class EnsembleDescriptor(Descriptor):

    def __init__(self, **kwargs):
        super(EnsembleDescriptor, self).__init__(**kwargs)
        self.skl = None

    def new(self, skl):
        new_obj = super(EnsembleDescriptor, self).new()
        new_obj.skl = skl
        return new_obj

    @property
    def attributes(self):
        attributes = list(self._attributes)

        for name, d, s in self.get_models():
            attrs = d.attributes
            for attr in attrs:
                d = copy.deepcopy(attr)
                d['name'] = name+'__'+d['name']
                attributes.append(d)
        return attributes

    def get_attribute(self, skl, attribute):
        if attribute in self._attributes:
            return getattr(skl, attribute)

        first_split = attribute.find('__')
        model_name = attribute[:first_split]
        attribute = attribute[first_split+2:]
        for name, d, s in self.get_models():
            if name == model_name:
                return d.get_attribute(s, attribute)
        raise AttributeError('No model matching attribute prefix found')

    @property
    def parameters(self):
        params = dict(self._parameters)

        for name, d, s in self.get_models():
            pars = d.parameters
            for key, value in pars.items():
                d = copy.deepcopy(value)
                d['skl_name'] = name+'__'+d['skl_name']
                params[name+'__'+key] = d
        return params

    @property
    def types(self):
        types = dict(self._types)
        if self.skl is None:
            return types

        for name, d, s in self.get_models():
            tps = d.types
            for key, value in tps.items():
                d = copy.deepcopy(value)
                types[name+'__'+key] = d
        return types

    def get_models(self):
        """Returns list of (name, desc, skl) for each contained estimator"""
        raise NotImplementedError()

    def post_fit(self, skl):
        self.skl = skl
        for name, desc, s in self.get_models():
            desc.skl = s
            desc.post_fit(s)

    def visualize(self, skl, layout):
        self._select_listview = QtGui.QListWidget()
        self._select_listview.setMinimumWidth(50)

        self._vsplitter = QtGui.QSplitter()
        self._vsplitter.setOrientation(Qt.Vertical)
        self._vsplitter_layout = QtGui.QVBoxLayout()
        self._vsplitter.setLayout(self._vsplitter_layout)

        self._models_layout = QtGui.QVBoxLayout()
        self._models_layout.addWidget(self._vsplitter)
        self._models_group = QtGui.QGroupBox()
        self._models_group.setLayout(self._models_layout)

        self._hsplitter = QtGui.QSplitter()
        self._hsplitter.addWidget(self._select_listview)
        self._hsplitter.addWidget(self._models_group)
        self._hsplitter.setSizes([50, 400])
        self._hsplitter.setCollapsible(0, False)
        self._hsplitter.setCollapsible(1, False)
        self._hsplitter.setHandleWidth(1)
        self._hsplitter.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Expanding)
        layout.addWidget(self._hsplitter)

        for name, d, s in self.get_models():
            self._select_listview.addItem(six.text_type(name))

        def index_changed(index):
            vsplitter = self._vsplitter
            # Delete all old content
            for old_idx in range(vsplitter.count())[::-1]:
                #wdg = vlayout.itemAt(old_idx).widget()
                wdg = vsplitter.widget(old_idx)
                wdg.deleteLater()
                #vlayout.removeWidget(wdg)
                #wdg.deleteLater()  #.setParent(None)

            # Render new visualization
            models = list(self.get_models())
            if len(models) == 0:
                vsplitter.addWidget(QtGui.QLabel(
                    "No scikit-learn model available"))
                return

            name, d, s = models[index]
            self._models_group.setTitle(d.name)
            if s is not None:
                set_model_tooltip(d, s, self._models_group)
                d.visualize(s, vsplitter)
            else:
                vsplitter.addWidget(QtGui.QLabel(
                    "No scikit-learn model available"))

        index_changed(0)
        self._select_listview.currentRowChanged[int].connect(index_changed)

class VotingClassifierDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(VotingClassifierDescriptor, self).__init__(**kwargs)
        self.set_children([],[])

    def set_children(self, names, descriptors):
        self._descs = descriptors
        self._names = names

    def set_x_names(self, x_names):
        self.x_names = x_names
        for d in self._descs:
            d.set_x_names(x_names)

    def set_y_names(self, y_names):
        self.y_names = y_names
        for d in self._descs:
            d.set_y_names(y_names)

    def get_models(self):
        skl = self.skl
        names = self._names
        descs = self._descs
        try:
            skls = skl.estimators_
        except AttributeError:
            return [(name, desc, None) for name, desc in zip(names, descs)]
        return list(zip(names, descs, skls))

class MultiOutputClassifierDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(MultiOutputClassifierDescriptor, self).__init__(**kwargs)
        self.set_child(None)
        self._descriptors = None

    def set_child(self, descriptor):
        self._desc = descriptor

    def set_x_names(self, x_names):
        self.x_names = x_names
        if self._descriptors is not None:
            for d in self._descriptors:
                d.set_x_names(self.x_names)
                d.set_y_names(self.y_names)

    def set_y_names(self, y_names):
        self.y_names = y_names
        if self._descriptors is None:
            self._descriptors = [copy.deepcopy(self._desc) for _ in y_names]
        for d in self._descriptors:
            d.set_x_names(self.x_names)
            d.set_y_names(self.y_names)

    def get_models(self):
        skl = self.skl
        names = self.y_names
        if names is None:
            return []

        descs = self._descriptors
        if descs is None:
            return []
        try:
            skls = skl.estimators_
        except AttributeError:
            return [(name, desc, None) for name, desc in zip(names, descs)]
        return list(zip(names, descs, skls))
