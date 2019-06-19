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

import numpy as np
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import sklearn
import sklearn.base
import sklearn.datasets
import sklearn.exceptions

from sympathy.api import node
from sympathy.api import ParameterView
from sympathy.api.nodeconfig import Port
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags

from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.model import ModelPort, encode, decode

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType


class Export(node.Node):
    name = 'Export Model'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'export.svg'
    description = 'Exports a model to disk'
    nodeid = 'org.sysess.sympathy.machinelearning.export'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([Port.Datasource('Datasource', name='filename'),
                    ModelPort('Input model', 'in-model')])
    outputs = Ports([])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        in_model = node_context.input['in-model']
        datasource = node_context.input['filename']
        pathname = datasource.decode_path()

        in_model.load()
        with open(pathname, 'wb') as f:
            f.write(encode(in_model.get()))


class Import(node.Node):
    name = 'Import Model'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'import.svg'
    description = 'Imports a model from disk'
    nodeid = 'org.sysess.sympathy.machinelearning.import'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([Port.Datasource('Datasource', name='filename')])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        out_model = node_context.output['out-model']
        datasource = node_context.input['filename']
        pathname = datasource.decode_path()

        with open(pathname, 'rb') as f:
            out_model.set(decode(f.read()))


datasets = {
    'Boston': sklearn.datasets.load_boston,
    'Diabetes': sklearn.datasets.load_diabetes,
    'Digits': sklearn.datasets.load_digits,
    'Iris': sklearn.datasets.load_iris,
    'LFW Faces': None,
    'linnerud': sklearn.datasets.load_linnerud,
}
# Datasets only available in sklearn 0.19+
try:
    datasets['wine'] = sklearn.datasets.load_wine
except AttributeError:
    pass

lfw_description = """
WARNING: Loading this dataset for the first time will download circa
230 MB of images from the internet.

Loader for the Labeled Faces in the Wild (LFW) people dataset

This dataset is a collection of JPEG pictures of famous people
collected on the internet, all details are available on the official
website:

    http://vis-www.cs.umass.edu/lfw/

Each picture is centered on a single face. Each pixel of each channel
(color in RGB) is encoded by a float in range 0.0 - 1.0.

The task is called Face Recognition (or Identification): given the
picture of a face, find the name of the person given a training set
(gallery).

The original images are 250 x 250 pixels, but the default slice and
resize arguments reduce them to 74 x 62.  """


class ExampleParameterWidget(ParameterView):
    def __init__(self, node_context, parent=None):
        super(ParameterView, self).__init__(parent=parent)
        self._parameters = node_context.parameters
        self._validator = None

        self.example_sel = QtGui.QComboBox()
        self.description_text = QtGui.QTextEdit("")
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumSize(480, 300)

        self.lfw_group = QtGui.QGroupBox("Labeled Faces in the Wild")
        self.lfw_vbox = QtGui.QVBoxLayout()
        self.lfw_group.setLayout(self.lfw_vbox)

        self.names = sorted(datasets.keys())
        for pos, name in enumerate(self.names):
            self.example_sel.addItem(name)
        # Set initially selected example
        index = self.example_sel.findText(self._parameters['dataset'].value,
                                          QtCore.Qt.MatchFixedString)
        if index < 0:
            index = 0
        self.example_sel.setCurrentIndex(index)
        self.example_sel.currentIndexChanged.connect(self.example_selected)
        self.example_selected(index)

        # Add to layout
        self.options_layout = QtGui.QVBoxLayout()
        self.options_layout.addWidget(self.example_sel)
        self.options_layout.addWidget(self.description_text)
        self.options_layout.addWidget(self.lfw_group)
        self.options_layout.addStretch(1)
        self.setLayout(self.options_layout)
        self.options_layout.setStretchFactor(self.description_text, 100)
        def param_widget(label, _name, _type):
            widget = QtGui.QWidget()
            hbox = QtGui.QHBoxLayout()
            widget.setLayout(hbox)
            label_widget = QtGui.QLabel(label)
            if isinstance(_type, BoolType):
                editor_widget = QtGui.QCheckBox()
            else:
                editor_widget = QtGui.QLineEdit()
            hbox.addWidget(label_widget)
            hbox.addStretch(1)
            hbox.addWidget(editor_widget)

            def text_updated(widget_=editor_widget, _type=_type):
                txt = widget_.text()
                try:
                    value = _type.from_string(txt)
                    self._parameters[_name].value = value
                except ValueError:
                    editor_widget.setText(
                        _type.to_string(node_context.parameters[name].value))

            def bool_updated(state, widget_=editor_widget, _type=_type):
                self._parameters[_name].value = bool(state)

            if isinstance(_type, BoolType):
                editor_widget.stateChanged.connect(bool_updated)
                if node_context.parameters[_name].value:
                    editor_widget.setCheckState(QtCore.Qt.Checked)
                else:
                    editor_widget.setCheckState(QtCore.Qt.Unchecked)
            else:
                editor_widget.editingFinished.connect(text_updated)
                editor_widget.setText(
                    _type.to_string(node_context.parameters[_name].value))
            editor_widget.setToolTip(_type.description())
            return widget

        class_names = param_widget('Class names', 'classnames',
                                   BoolType())
        self.options_layout.addWidget(class_names)
        class_names.setToolTip('Attempts to use class names as Y')

        self.lfw_vbox.addWidget(
            param_widget('color', 'color', BoolType()))
        self.lfw_vbox.addWidget(
            param_widget('Resize factor: ', 'resize',
                         FloatType(min_value=0.0)))
        self.lfw_vbox.addWidget(
            param_widget('Min pictures per person: ', 'min_pictures',
                         IntType(min_value=0)))

    def example_selected(self, index):
        name = self.names[index]
        self._parameters['dataset'].value = name
        if name == 'LFW Faces':
            self.description_text.setText(lfw_description)
            self.lfw_group.show()
        else:
            dataset_fn = datasets[name]
            dataset = dataset_fn()
            try:
                self.description_text.setText(dataset.DESCR)
            except AttributeError:
                self.description_text.setText('Dataset lack a description')
            self.lfw_group.hide()


class ExampleDatasets(node.Node):
    name = 'Example datasets'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'example_datasets.svg'
    description = 'Exposes the example datasets from sklearn'
    nodeid = 'org.sysess.sympathy.machinelearning.example_datasets'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([])
    outputs = Ports([Port.Table('X', name='X'), Port.Table('Y', name='Y')])
    parameters = node.parameters()
    parameters.set_string(
        'dataset', value='Iris', label='Dataset',
        description='Choose from one of the default toy datasets')
    parameters.set_boolean(
        'classnames', value=True, label='Class names',
        description='Attempts to use class names as Y')
    parameters.set_boolean(
        'color', value=False, label='color')
    parameters.set_integer(
        'min_pictures', value=10, label='min_pictures',
        description=(
            'Minimum number of pictures per person required for including '
            'a person in the LFW dataset'))
    parameters.set_float(
        'resize', value=0.5, label='resize',
        description=(
            'Resize LFW pictures, default 0.5 give size 62x47 images'))
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def exec_parameter_view(self, node_context):
        return ExampleParameterWidget(node_context)

    def execute(self, node_context):
        out_X = node_context.output['X']
        out_Y = node_context.output['Y']
        dataset_name = node_context.parameters['dataset'].value
        min_pictures = node_context.parameters['min_pictures'].value
        color = node_context.parameters['color'].value
        resize = node_context.parameters['resize'].value

        if dataset_name != 'LFW Faces':
            dataset = datasets[dataset_name]()
        else:
            dataset = sklearn.datasets.fetch_lfw_people(
                min_faces_per_person=min_pictures, resize=resize, color=color)

        classnames = node_context.parameters['classnames'].value

        X = dataset.data
        Y = dataset.target

        out_X.set_name(dataset_name+" X")
        out_Y.set_name(dataset_name+" Y")

        try:
            X_names = dataset.feature_names
        except AttributeError:
            X_names = ["X{0}".format(i) for i in range(X.shape[1])]

        for i, name in enumerate(X_names):
            out_X.set_column_from_array(name, X[:, i])

        if classnames:
            try:
                target_names = dataset.target_names
                Y = target_names[Y]
            except (TypeError, AttributeError):
                pass

        if len(Y.shape) < 2:
            out_Y.set_column_from_array("Y", Y)
        else:
            for i in range(Y.shape[1]):
                out_Y.set_column_from_array("Y{0}".format(i), Y[:, i])


class MakeBlobs(node.Node):
    name = 'Generate dataset blobs'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Generates an artificial dataset useful for testing '
        'clustering algorithms')
    nodeid = 'org.sysess.sympathy.machinelearning.generate_blobs'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([])
    outputs = Ports([Port.Table('X', name='X'), Port.Table('Y', name='Y')])
    parameters = node.parameters()
    parameters.set_integer(
        'n_samples', value=100, label='n_samples',
        description=(
            'The total number of points equally divided among clusters.'))
    parameters.set_integer(
        'n_features', value=2, label='n_features',
        description='The number of features for each sample.')
    parameters.set_integer(
        'centers', value=3, label='centers', description='Number of clusters.')
    parameters.set_float(
        'cluster_std', value=2.0, label='cluster_std',
        description='Standard deviation of the clusters.')
    parameters.set_float(
        'center_min', value=-10.0, label='center_min',
        description='Smallest allowed coordinate for the generated centers')
    parameters.set_float(
        'center_max', value=10.0, label='center_max',
        description='Largest allowed coordinate for the generated centers')
    parameters.set_boolean(
        'shuffle', value=True, label='shuffle',
        description='Shuffle datapoints (otherwise given in cluster order)')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_X = node_context.output['X']
        out_Y = node_context.output['Y']

        out_X.set_name("X")
        out_Y.set_name("Y")

        kwargs = {}
        kwargs['center_box'] = (node_context.parameters['center_min'].value,
                                node_context.parameters['center_max'].value)
        kn = ['n_samples', 'n_features', 'centers', 'cluster_std', 'shuffle']
        for name in kn:
            kwargs[name] = node_context.parameters[name].value
        X, Y = sklearn.datasets.make_blobs(**kwargs)

        X_names = ["X{0}".format(i) for i in range(X.shape[1])]
        for i, name in enumerate(X_names):
            out_X.set_column_from_array(name, X[:, i])
        out_Y.set_column_from_array("Y", Y)


class MakeBlobsFromTable(node.Node):
    name = 'Generate dataset blobs from table'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Takes a table describing blob center positions and optionally '
        'standard deviations and generates a random dataset. Rows in table'
        'corresponds to cluster number, and columns to the number of '
        'features in the datasets.')
    nodeid = 'org.sysess.sympathy.machinelearning.generate_blobs_from_table'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([Port.Table('C', name='C')])
    outputs = Ports([Port.Table('X', name='X'), Port.Table('Y', name='Y')])
    parameters = node.parameters()
    parameters.set_integer(
        'n_samples', value=100, label='n_samples',
        description=(
            'The total number of points equally divided among clusters.'))
    parameters.set_integer(
        'n_features', value=2, label='n_features',
        description='The number of features for each sample.')
    parameters.set_string(
        'cluster_std', value="2.0", label='cluster_std',
        description=('Column name used to give standard deviation for each '
                     'cluster. If empty or a float number then the same value '
                     'is used for each cluster'))
    parameters.set_boolean(
        'shuffle', value=True, label='shuffle',
        description='Shuffle datapoints (otherwise given in cluster order)')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_C = node_context.input['C']
        out_X = node_context.output['X']
        out_Y = node_context.output['Y']

        kwargs = {}
        try:
            std = float(node_context.parameters['cluster_std'].value)
            ignore_col = None
        except ValueError:
            name = node_context.parameters['cluster_std'].value
            std = in_C.get_column_to_array(name)
            ignore_col = name

        cols = []
        X_names = []
        for name in in_C.column_names():
            if name != ignore_col:
                cols.append(in_C.get_column_to_array(name))
                X_names.append(name)
        kwargs['centers'] = np.array(cols).T
        kwargs['cluster_std'] = std
        for name in ['n_samples', 'n_features', 'shuffle']:
            kwargs[name] = node_context.parameters[name].value
        X, Y = sklearn.datasets.make_blobs(**kwargs)

        for i, name in enumerate(X_names):
            out_X.set_column_from_array(name, X[:, i])
        out_Y.set_column_from_array("Y", Y)


class MakeClassification(node.Node):
    name = 'Generate classification dataset'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'dataset_classes.svg'
    description = """
Generates an artificial dataset useful for testing classification algorithms.

Generate a random n-class classification problem.
This initially creates clusters of points normally distributed (std=1) about
vertices of a 2 * class_sep-sided hypercube, and assigns an equal number of
clusters to each class. It introduces interdependence between these features
and adds various types of further noise to the data.

Prior to shuffling, X stacks a number of these primary 'informative' features,
'redundant' linear combinations of these, 'repeated' duplicates of sampled
features, and arbitrary noise for any remaining features.
"""
    nodeid = 'org.sysess.sympathy.machinelearning.generate_classification'
    tags = Tags(Tag.MachineLearning.IO)

    inputs = Ports([])
    outputs = Ports([Port.Table('X', name='X'), Port.Table('Y', name='Y')])
    parameters = node.parameters()
    parameters.set_integer(
        'n_samples', value=100, label='n_samples',
        description='The total number of samples generated.')
    parameters.set_integer(
        'n_features', value=20, label='n_features',
        description='The number of features for each sample.')
    parameters.set_integer(
        'n_informative', value=2, label='n_informative',
        description="""The number of informative features.

Each class is composed of a number of gaussian clusters each located
around the vertices of a hypercube in a subspace of dimension
n_informative. For each cluster, informative features are drawn
independently from N(0, 1) and then randomly linearly combined within
each cluster in order to add covariance. The clusters are then placed
on the vertices of the hypercube.""")
    parameters.set_integer(
        'n_redundant', value=2, label='n_redundant',
        description=(
            'The number of redundant features. These features are generated '
            'as random linear combinations of the informative features.'))
    parameters.set_integer(
        'n_repeated', value=0, label='n_repeated',
        description=(
            'The number of duplicated features, drawn randomly from the '
            'informative and the redundant features.'))
    parameters.set_integer(
        'n_classes', value=2, label='n_classes',
        description=('The number of classes (labels) for the '
                     'classification problem'))
    parameters.set_integer(
        'n_clusters_per_class', value=2, label='n_clusters_per_class',
        description=(
            'The number of classes (or labels) of the classification problem.')
    )
    parameters.set_string(
        'weights', value="None", label='weights',
        description="""Comma separated list of float weights for each class.

Determines the proportions of samples assigned to each class. If None,
then classes are balanced. Note that if len(weights) == n_classes - 1,
then the last class weight is automatically inferred. More than
n_samples samples may be returned if the sum of weights exceeds 1. """)
    parameters.set_float(
        'flip_y', value=0.01, label='flip_y',
        description=('The fraction of samples whose class are '
                     'randomly exchanged'))
    parameters.set_float(
        'class_sep', value=1.0, label='class_sep',
        description='Factor multiplying the hypercube dimension')
    parameters.set_string(
        'shift', value="0.0", label='shift',
        description=(
            'Shift features by the specified comma separated value(s). '
            'If None, then features are shifted by a random value drawn in:'
            '  [-class_sep, class_sep].'))
    parameters.set_string(
        'scale', value="1.0", label='scale',
        description=(
            'Multiply features by the specified comma separated value(s). '
            'If None, then features are scaled by a random value drawn in:'
            '  [1, 100].\nNote that scaling happens after shifting.'))
    parameters.set_boolean(
        'hypercube', value=True, label='hypercube',
        description=(
            'If true clusters are put on vertices of a hypercube, '
            'otherwise a random polytope'))
    parameters.set_boolean(
        'shuffle', value=True, label='shuffle',
        description='Shuffle datapoints (otherwise given in cluster order)')

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_X = node_context.output['X']
        out_Y = node_context.output['Y']

        kwargs = {}
        for name in node_context.parameters.keys():
            kwargs[name] = node_context.parameters[name].value

        for name in ['weights', 'shift', 'scale']:
            string = kwargs[name]
            if string.lower() == 'none':
                kwargs[name] = None
                continue
            string = string.replace(',', ' ')
            arg = [float(word) for word in string.split()]
            if len(arg) == 1:
                kwargs[name] = arg
            elif name == 'weights':
                kwargs[name] = arg
            else:
                kwargs[name] = np.array(arg)

        X, Y = sklearn.datasets.make_classification(**kwargs)

        X_names = ["X{0}".format(i) for i in range(X.shape[1])]
        for i, name in enumerate(X_names):
            out_X.set_column_from_array(name, X[:, i])
        out_Y.set_column_from_array("Y", Y)
