# Copyright (c) 2016, Combine Control Systems AB
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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)

import json
import uuid

from sympathy.api import qt
from sympathy.api import ParameterView
from sylib.figure import models, util
from sylib.tree_model import qt_model, models as base_models

QtCore = qt.QtCore
QtGui = qt.QtGui

MIME = {
    'layout_tree_item_id': 'application-x-sympathy/figure.layout.tree.item.id',
    'layout_tree_new_item':
        'application-x-sympathy/figure.layout.tree.new.item',
    'instance': 'application-x-sympathy/figure.instance'
}


TOOLBAR_ITEMS = [
    'separator',
    models.Axes,
    'separator',
    models.LinePlot,
    models.ScatterPlot,
    models.BarPlot,
    models.HistogramPlot,
    models.TimelinePlot,
    models.HeatmapPlot,
    models.BoxPlot,
    models.PieChart,
    models.Annotation,
    'separator',
    models.BarContainer,
    models.HistogramContainer,
    'separator',
    models.Iterator,
    'separator',
    models.Legend,
    models.Grid,
]


ITEM_TYPE_TO_CLASS = {
    i.node_type: i for i in TOOLBAR_ITEMS if i != 'separator'}


class DataModel(object):
    def __init__(self, data, data_table=None):
        self.instance = uuid.uuid4().bytes
        self.model = data
        self.root = models.Root(data)
        self.root.set_data_table(data_table)


class ParameterTreeView(qt_model.BaseParameterTreeView):
    def __init__(self, input_table, mime=MIME, parent=None):
        super(ParameterTreeView, self).__init__(input_table, mime, parent)
        self.completer_models = {
            'default':
                (qt_model.SyTableTreeCompleterModel,
                 (self._input_table, ),
                 {'parent': self})
        }

    def add(self, item_cls):
        selected_indices = self.selectedIndexes()
        model = self.model()
        figure_node = self.model().root_item()
        figure_index = model.item_to_index(figure_node)
        if selected_indices:
            selected_index = selected_indices[0]
        else:
            self.setCurrentIndex(figure_index)
            selected_index = figure_index
        selected_item = model.index_to_item(selected_index)

        parent_axes = selected_item.find_first_parent_node_with_class(
            models.Axes)
        if item_cls != models.Axes:
            if not figure_node.has_axes():
                parent_axes = self.add_child(
                    figure_node, models.Axes, figure_index)
            elif parent_axes is None:
                parent_axes = [c for c in figure_node.children if
                               isinstance(c, models.Axes)][0]

        plot_nodes = models.BasePlot, models.BasePlotContainer

        if item_cls in selected_item.valid_children():
            parent_node = selected_item
        elif issubclass(item_cls, models.Axes):
            parent_node = figure_node
        elif issubclass(item_cls, (models.Grid, models.Legend)):
            parent_node = parent_axes
        elif issubclass(item_cls, plot_nodes):
            if isinstance(selected_item, plot_nodes):
                parent_node = selected_item.parent
            else:
                parent_node = parent_axes.plot_container
        elif item_cls not in selected_item.valid_children():
            parent_node = selected_item.parent
        else:
            parent_node = selected_item
        parent_index = model.item_to_index(parent_node)

        if (item_cls in parent_node.valid_children() and
                item_cls in parent_node.get_available_children()):
            new_item = self.add_child(parent_node, item_cls, parent_index)
            new_item_idx = model.item_to_index(new_item)
            self.setCurrentIndex(new_item_idx)

    def drag_move_event_handling(self, event, item_class, index):
        if index.isValid():
            drop_indicator_position = self.dropIndicatorPosition()
            parent_item = index.model().data(index, QtCore.Qt.UserRole)
            if parent_item is None:
                event.ignore()
                return
            if drop_indicator_position != QtGui.QAbstractItemView.OnItem:
                # If the drop indicator is not on the item we need to get the
                # parent item in the tree instead.
                parent_item = parent_item.parent
            if item_class in parent_item.get_available_children():
                event.accept()
            else:
                event.ignore()
        else:
            # Only axes items are allowed outside tree (root level).
            # If Plots or PlotContainers are dragged in and no Axes exists, one
            # will be created automatically.
            root = self.model().model.root
            figure = root.find_all_nodes_with_class(models.Figure)[0]
            allowed_super_cls = (models.BasePlot, models.BasePlotContainer)
            if item_class in figure.get_available_children():
                event.accept()
            elif (issubclass(item_class, allowed_super_cls) and
                    not figure.has_axes()):
                # create axes
                axes = models.Axes.create_empty_instance(figure)
                model = self.model()
                figure_index = model.index(0, 0)
                model.insert_node(
                    axes, figure, figure_index, len(figure.children))
                # add item to axes
                event.accept()
            else:
                event.ignore()


class FigureFromTableWidget(ParameterView):
    def __init__(self, input_table, parameters, parent=None):
        super(FigureFromTableWidget, self).__init__(parent=parent)

        self.input_table = input_table
        self.parameters = parameters

        parsed_config = util.parse_configuration(
            json.loads(parameters['parameters'].value))
        self._data_model = DataModel(parsed_config,
                                     data_table=self.input_table)
        self._model = qt_model.TreeItemModel(
            self._data_model, root_cls=models.Figure,
            item_type_to_class=ITEM_TYPE_TO_CLASS, mime=MIME)

        self._init_gui()
        self._init_from_parameters()

    def _init_gui(self):
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.param_tree = ParameterTreeView(
            self.input_table, mime=MIME, parent=self)
        self.param_tree.setModel(self._model)

        self.toolbar = qt_model.BaseItemsToolBar(
            self.param_tree, TOOLBAR_ITEMS, mime=MIME, parent=self)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.param_tree)

        self.setLayout(layout)

    def resizeEvent(self, event):
        super(FigureFromTableWidget, self).resizeEvent(event)
        self.param_tree.resizeColumnToContents(0)

    def _init_from_parameters(self):
        self.param_tree.resizeColumnToContents(0)

        # add one axes if empty model
        if not self._model.root_item().has_axes():
            parent_item = self._model.root_item()
            parent_index = self._model.index(-1, -1)
            item_class = self._model.item_type_to_class['axes']
            if item_class not in parent_item.valid_children():
                return False
            new_item = item_class.create_empty_instance(parent_item)

            self._model.beginInsertRows(parent_index, 0, 0)
            base_models.insert_node(new_item, parent_item, 0)
            self._model.endInsertRows()

        # expand all axes
        num_axes = self._model.rowCount()
        for i in range(num_axes):
            index = self._model.index(i, 0)
            self.param_tree.setExpanded(index, True)
            # expand all Plots
            for row in range(self._model.rowCount(index)):
                child_index = self._model.index(row, 0, index)
                item = self._model.index_to_item(child_index)
                if isinstance(item, models.Plots):
                    self.param_tree.setExpanded(child_index, True)

    def save_parameters(self):
        exported_config = self._data_model.root.export_config()
        self.parameters['parameters'].value = json.dumps(exported_config)
