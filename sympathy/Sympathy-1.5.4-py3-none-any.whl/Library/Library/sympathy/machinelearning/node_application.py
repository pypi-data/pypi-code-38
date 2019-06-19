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
import inspect
import numpy as np
import warnings

import sklearn
import sklearn.base
import sklearn.exceptions
import sklearn.feature_selection
import scipy.sparse

from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError, sywarn

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType

from sylib.machinelearning.utility import data_to_table
from sylib.machinelearning.utility import table_to_array
from sylib.machinelearning.utility import array_to_table


class Fit(node.Node):
    name = 'Fit'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'fit.svg'
    description = (
        'Trains a model. Use "Create Input Port > Y" for supervised training')
    nodeid = 'org.sysess.sympathy.machinelearning.fit'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('X', name='X'),
                    Port.Custom('table', 'Y', name='Y0', n=(0, 1, 1)),
                    Port.Custom('table', 'sample_weights',
                                name='sample_weights', n=(0, 1))])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbls = node_context.input.group('Y0')
        in_model = node_context.input['in-model']
        out_model = node_context.output['out-model']
        sample_weights = node_context.input.group('sample_weights')

        if len(Y_tbls) > 0:
            Y_tbl = Y_tbls[0]
            Y = table_to_array(Y_tbls[0], unitary=True)
        else:
            Y = None
            Y_tbl = None

        if len(sample_weights) > 0:
            sample_weight = table_to_array(sample_weights[0], unitary=True)
        else:
            sample_weight = None

        out_model.source(in_model)
        out_model.load()
        model = out_model.get_skl()
        X = table_to_array(X_tbl)

        # Check if we can fit in a progress_update function
        kwargs = {}
        args, _, _, _ = inspect.getargspec(model.fit)
        if 'progress_fn' in args:
            kwargs['progress_fn'] = lambda i: self.set_progress(i)

        with warnings.catch_warnings():
            warnings.simplefilter(
                'ignore', sklearn.exceptions.ConvergenceWarning)

            if Y is None:
                if sample_weight is None:
                    model.fit(X, **kwargs)
                else:
                    model.fit(X, sample_weight=sample_weight, **kwargs)
            else:
                if sample_weight is None:
                    model.fit(X, Y, **kwargs)
                else:
                    model.fit(X, Y, sample_weight=sample_weight, **kwargs)

        desc = out_model.get_desc()
        desc.set_x_names(X_tbl.column_names())
        if Y_tbl is not None:
            desc.set_y_names(Y_tbl.column_names())
        desc.post_fit(model)
        out_model.save()


class FitText(node.Node):
    name = 'Fit Texts'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'fit_text.svg'
    description = (
        'Fits a model using lists of texts. '
        'Use "Create Input Port > Y" for supervised training')
    nodeid = 'org.sysess.sympathy.machinelearning.fit_text'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Custom('[text]', 'X', name='X'),
                    Port.Custom('table', 'Y', name='Y0', n=(0, 1, 1))])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        Y_tbls = node_context.input.group('Y0')
        in_model = node_context.input['in-model']
        out_model = node_context.output['out-model']

        X = [x.get() for x in node_context.input['X']]

        if len(Y_tbls) > 0:
            Y_tbl = Y_tbls[0]
        else:
            Y_tbl = None

        out_model.source(in_model)
        out_model.load()
        model = out_model.get_skl()

        with warnings.catch_warnings():
            warnings.simplefilter(
                'ignore', sklearn.exceptions.ConvergenceWarning)

            if Y_tbl is None:
                model.fit(X)
            else:
                Y = table_to_array(Y_tbl, unitary=True)
                model.fit(X, Y)

        desc = out_model.get_desc()
        desc.set_x_names(['corpus'])
        if Y_tbl is not None:
            desc.set_y_names(Y_tbl.column_names())
        desc.post_fit(model)
        out_model.save()


class Predict(node.Node):
    name = 'Predict'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'predict.svg'
    description = 'Uses a model to predict Y given X'
    nodeid = 'org.sysess.sympathy.machinelearning.predict'
    tags = Tags(Tag.MachineLearning.Apply)

    parameters = node.parameters()
    parameters.set_boolean(
        'pass_x', label='Pass through X', value=False,
        description=(
            'Passes through a copy of X in addition to the predicted values'))

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('X', name='X')])
    outputs = Ports([Port.Table('Y', name='Y')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.output['Y']
        in_model = node_context.input['in-model']
        pass_x = node_context.parameters['pass_x'].value

        in_model.load()
        model = in_model.get_skl()
        desc = in_model.get_desc()
        X = table_to_array(X_tbl)
        try:
            Y = desc.predict(model, X)
        except TypeError:
            raise SyDataError(
                "Model does not implement the 'predict' function")
            return

        if pass_x:
            for col in X_tbl.cols():
                Y_tbl.set_column_from_array(col.name, col.data)

        if len(Y.shape) < 2:
            Y = Y.reshape(Y.shape + (1,))
        y_names = in_model.get_desc().y_names
        if y_names is None:
            y_names = ["y{0}".format(i) for i in range(Y.shape[1])]
        for i, name in enumerate(y_names):
            Y_tbl.set_column_from_array(name, Y[:, i])


class PredictProbabilities(node.Node):
    name = 'Predict Probabilities'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'probabilities.svg'
    description = (
        'Uses a model to predict Y given X and returns the estimated'
        'probabilities for each class in Y')
    nodeid = 'org.sysess.sympathy.machinelearning.predict_proba'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('X', name='X')])
    outputs = Ports([Port.Table('Y', name='Y')])
    parameters = node.parameters()
    parameters.set_string(
        'names method',
        label='Output names',
        value='From classes',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'From classes', 'By index', 'From model Y names']))
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.output['Y']
        in_model = node_context.input['in-model']
        names = node_context.parameters['names method'].value

        in_model.load()
        model = in_model.get_skl()
        X = table_to_array(X_tbl)
        try:
            Y = model.predict_proba(X)
        except TypeError:
            raise SyDataError(
                "Model does not implement the 'predict' function")
            return

        if type(Y) == list:
            Y = np.concatenate(Y, axis=1)
        if len(Y.shape) < 2:
            Y = Y.reshape(Y.shape+(1,))

        y_names = ["Y{0}".format(i) for i in range(Y.shape[1])]
        if names == 'From classes':
            try:
                y_names = [str(classname) for classname in model.classes_]
            except AttributeError:
                pass
        elif names == 'From model Y names':
            cols = in_model.get_desc().y_names
            y_names[:len(cols)] = cols

        for i, name in enumerate(y_names):
            Y_tbl.set_column_from_array(name, Y[:, i])


class DecisionFunction(node.Node):
    name = 'Decision Function'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'decision_function.svg'
    description = (
        'Applies the decision function (if available) of a trained model '
        'to return a scalar for each class of outputs')
    nodeid = 'org.sysess.sympathy.machinelearning.decision_function'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('X', name='X')])
    outputs = Ports([Port.Table('Y', name='Y')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.output['Y']
        in_model = node_context.input['in-model']

        in_model.load()
        model = in_model.get_skl()
        X = table_to_array(X_tbl)
        try:
            Y = model.decision_function(X)
        except TypeError:
            raise SyDataError("Model does not implement 'decision_function'")
            return

        if len(Y.shape) < 2:
            Y = Y.reshape(Y.shape + (1,))
        y_names = in_model.get_desc().y_names
        if y_names is not None and len(y_names) < Y.shape[1]:
            y_names = None
        if y_names is None:
            try:
                y_names = model.classes_
            except AttributeError:
                # Well, we tried - use fallback names
                pass
        if y_names is None:
            y_names = ["y{0}".format(i) for i in range(Y.shape[1])]
        for i, name in enumerate(y_names):
            Y_tbl.set_column_from_array(name, Y[:, i])


class FitTransform(node.Node):
    name = 'Fit Transform'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'transform.svg'
    description = (
        'Fits a transform model to the given data and computes '
        'the transformed data. ')
    nodeid = 'org.sysess.sympathy.machinelearning.fit_transform'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('Input table', name='input'),
                    Port.Custom('table', 'Y', name='Y', n=(0, 1, 0))])
    outputs = Ports([ModelPort('Output model', 'out-model'),
                     Port.Table('Output table', name='output')])
    parameters = node.parameters()
    parameters.set_string(
        'names method', label='Output names', value='From model',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'Copy from input', 'By index', 'From model']))
    parameters.set_boolean(
        'transpose', value=False, label='Transpose output',
        description='Transposes output data, suitable for large '
        'number of features (eg. word counts)')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_tbl = node_context.input['input']
        y_tbls = node_context.input.group('Y')
        out_tbl = node_context.output['output']
        in_model = node_context.input['in-model']
        out_model = node_context.output['out-model']
        names = node_context.parameters['names method'].value
        transpose = node_context.parameters['transpose'].value

        out_model.source(in_model)
        out_model.load()
        transform = out_model.get_skl()
        X = table_to_array(in_tbl)
        if len(y_tbls) > 0:
            Y = table_to_array(y_tbls[0], unitary=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    'ignore', sklearn.exceptions.ConvergenceWarning)

                if len(y_tbls) > 0:
                    Xprim = transform.fit_transform(X, Y)
                else:
                    Xprim = transform.fit_transform(X)
        except TypeError as e:
            sywarn(e)
            raise SyDataError(
                'Model does not implement transforms with only one input')
            return

        desc = out_model.get_desc()
        desc.set_x_names(in_tbl.column_names())
        if len(y_tbls) > 0:
            desc.set_y_names(y_tbls[0].column_names())

        desc.post_fit(transform)
        out_model.save()

        if names == 'Copy from input':
            cols = in_tbl.column_names()
        elif names == 'From model' and desc.xout_names is not None:
            cols = desc.xout_names
        else:
            cols = []
        Xprim = data_to_table(Xprim, cols, out_tbl, transpose=transpose)


class FitTransformText(node.Node):
    name = 'Fit Transform Text'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'transform_text.svg'
    description = (
        'Fits a transform model to the given text data and computes '
        'the transformed data. '
        'Use "Create Input Port > Y" for supervised training')
    nodeid = 'org.sysess.sympathy.machinelearning.fit_transform_text'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Custom('[text]', 'X', name='X')])
    outputs = Ports([ModelPort('Output model', 'out-model'),
                     Port.Table('Output table', name='output')])
    parameters = node.parameters()
    parameters.set_string(
        'names method', label='Output names', value='From model',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'By index', 'From model']))
    parameters.set_boolean(
        'transpose', value=False, label='Transpose output',
        description='Transposes output data, suitable for large '
        'number of features (eg. word counts)')

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_tbl = node_context.output['output']
        in_model = node_context.input['in-model']
        out_model = node_context.output['out-model']
        names = node_context.parameters['names method'].value
        transpose = node_context.parameters['transpose'].value

        X = [x.get() for x in node_context.input['X']]

        out_model.source(in_model)
        out_model.load()
        transform = out_model.get_skl()

        try:
            Xprim = transform.fit_transform(X)
        except TypeError:
            raise SyDataError(
                'Model does not implement transforms with only one input')
            return

        desc = out_model.get_desc()
        desc.post_fit(transform)
        out_model.save()

        if names == 'From model' and desc.y_names is not None:
            cols = desc.xout_names
        else:
            cols = []
        Xprim = data_to_table(Xprim, cols, out_tbl, transpose=transpose)


class Transform(node.Node):
    name = 'Transform'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'transform.svg'
    description = 'Applies a transformation model to the given data'
    nodeid = 'org.sysess.sympathy.machinelearning.transform'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('Input table', name='input')])
    outputs = Ports([Port.Table('Output table', name='output')])
    parameters = node.parameters()
    parameters.set_string(
        'names method', label='Output names', value='Copy from input',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'Copy from input', 'By index', 'From model']))
    parameters.set_boolean(
        'transpose', value=False, label='Transpose output',
        description='Transposes output data, suitable for large '
        'number of features (eg. word counts)')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_tbl = node_context.input['input']
        out_tbl = node_context.output['output']
        in_model = node_context.input['in-model']
        names = node_context.parameters['names method'].value
        transpose = node_context.parameters['transpose'].value

        in_model.load()
        transform = in_model.get_skl()
        desc = in_model.get_desc()
        X = table_to_array(in_tbl)
        try:
            Xprim = desc.transform(transform, X)
        except TypeError:
            raise SyDataError(
                'Given model does not implement transforms (one input)')
            return
        except sklearn.exceptions.NotFittedError as e:
            raise SyDataError(repr(e))

        if names == 'Copy from input':
            cols = in_tbl.column_names()
        elif names == 'From model' and desc.y_names is not None:
            cols = desc.xout_names
        else:
            cols = []
        Xprim = data_to_table(Xprim, cols, out_tbl, transpose=transpose)


class TransformText(node.Node):
    name = 'Transform Text'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'transform_text.svg'
    description = 'Applies a transformation model to the given text data'
    nodeid = 'org.sysess.sympathy.machinelearning.transform_text'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Custom('[text]', 'X', name='X')])
    outputs = Ports([Port.Table('Output table', name='output')])
    parameters = node.parameters()
    parameters.set_string(
        'names method', label='Output names', value='From model',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'By index', 'From model']))
    parameters.set_boolean(
        'transpose', value=False, label='Transpose output',
        description='Transposes output data, suitable for large '
        'number of features (eg. word counts)')

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out_tbl = node_context.output['output']
        in_model = node_context.input['in-model']
        names = node_context.parameters['names method'].value
        transpose = node_context.parameters['transpose'].value

        X = [x.get() for x in node_context.input['X']]

        in_model.load()
        transform = in_model.get_skl()
        desc = in_model.get_desc()
        try:
            Xprim = transform.transform(X)
        except TypeError:
            raise SyDataError(
                'Given model does not implement transforms (one input)')
            return
        except sklearn.exceptions.NotFittedError as e:
            raise SyDataError(repr(e))

        if scipy.sparse.issparse(Xprim):
            Xprim = Xprim.toarray()

        if len(Xprim.shape) < 2:
            Xprim = Xprim.reshape(Xprim.shape+(1,))

        if names == 'From model' and desc.y_names is not None:
            cols = desc.y_names
        else:
            cols = []

        Xprim = data_to_table(Xprim, cols, out_tbl, transpose=transpose)


class InverseTransform(node.Node):
    name = 'Inverse Transform'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'inverse_transform.svg'
    description = (
        'Applies the inverse of a transformation model to the given data')
    nodeid = 'org.sysess.sympathy.machinelearning.inverse_transform'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('Input table', name='input')])
    outputs = Ports([Port.Table('Output table', name='output')])
    parameters = node.parameters()
    parameters.set_string(
        'names method', label='Output names', value='Copy from input',
        description='Method used to generate output names',
        editor=node.Util.combo_editor(options=[
            'Copy from input', 'By index', 'From model']))
    parameters.set_boolean(
        'transpose', value=False, label='Transpose output',
        description='Transposes output data, suitable for large '
        'number of features (eg. word counts)')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_tbl = node_context.input['input']
        out_tbl = node_context.output['output']
        in_model = node_context.input['in-model']
        names = node_context.parameters['names method'].value
        transpose = node_context.parameters['transpose'].value

        in_model.load()
        transform = in_model.get_skl()
        desc = in_model.get_desc()
        X = table_to_array(in_tbl)
        try:
            Xprim = transform.inverse_transform(X)
        except TypeError:
            raise SyDataError(
                'Given model does not implement inverse transforms')
            return
        except sklearn.exceptions.NotFittedError as e:
            raise SyDataError(repr(e))

        if names == 'Copy from input':
            cols = in_tbl.column_names()
        elif names == 'From model' and desc.y_names is not None:
            cols = desc.x_names
        else:
            cols = []

        Xprim = data_to_table(Xprim, cols, out_tbl, transpose=transpose)


class Score(node.Node):
    name = 'Score'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'score.svg'
    description = (
        'Scores the model using given X and Y data. Exact semantics\n'
        'depends on the type of model (classifier, regressor, etc).')
    nodeid = 'org.sysess.sympathy.machinelearning.score'
    tags = Tags(Tag.MachineLearning.Metrics)

    parameters = node.parameters()
    parameters.set_boolean(
        'default method', label='Use built-in default scoring',
        value=True,
        description=(
            'Uses the default scoring method defined by the used model.\n'
            'Semantics of the scoring depend on the type of node\n\n'
            '(classifier, regressor, etc). Otherwise the problem is assumed\n'
            'to be a classification problem, a single predict call is\n'
            'made and extended information is given for each target. \n'
            'If model does not implement the predict function then a\n'
            'transform is used instead.'))

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('X', name='X'),
                    Port.Table('Y', name='Y')])
    outputs = Ports([Port.Table('Score', name='Score')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        in_model = node_context.input['in-model']
        score_tbl = node_context.output['Score']
        default_method = node_context.parameters['default method'].value

        in_model.load()
        model = in_model.get_skl()
        desc = in_model.get_desc()
        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)

        if list(desc.y_names) != list(Y_tbl.column_names()):
            sywarn('Column names for Y does not match those in model')

        if default_method:
            try:
                score = model.score(X, Y)
            except TypeError:
                raise SyDataError(
                    'Given model does not implement the "score" function')
            else:
                score_tbl.set_column_from_array('score', np.array([score]))
        else:
            try:
                Y_pred = model.predict(X)
            except TypeError:
                try:
                    Y_pred = model.transform(X)
                except TypeError:
                    raise SyDataError(
                        'Given model does not implement neither predict '
                        'nor transform')
            if len(Y_pred.shape) == 1:
                Y_pred = Y_pred.reshape(Y_pred.shape+(1,))
            if len(Y.shape) == 1:
                Y = Y.reshape(Y.shape+(1,))
            if Y.shape != Y_pred.shape:
                raise SyDataError(
                    'Shape of predicted Y-data {} does not match actual Y {}'
                    .format(Y_pred.shape, Y.shape))

            correct = Y == Y_pred
            score = np.all(correct, axis=1).mean()
            score_tbl.set_column_from_array('score', np.array([score]))
            if len(desc.y_names) > 1:
                for pos, name in enumerate(desc.y_names):
                    col = correct[:, pos]
                    score_tbl.set_column_from_array(
                        name, np.array([col.mean()]))


class SelectFromModel(SyML_abstract, node.Node):
    name = 'Select Features from Model'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'select_model.svg'
    description = (
        'Meta-transformer for selecting features based on importance weight. '
        'Only works for models with coef or feature_importances attributes.'
    )
    nodeid = 'org.sysess.sympathy.machinelearning.select_from_model'
    tags = Tags(Tag.MachineLearning.Apply)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'threshold',
         'type': UnionType([
             StringSelectionType(['median', 'mean']),
             FloatType(), NoneType()], default=None)},
    ], doc_class=sklearn.feature_selection.SelectFromModel)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([ModelPort('Model', 'model'),
                    Port.Table('in-data', name='in-data')])
    outputs = Ports([Port.Table('out-data', name='out-data'),
                     Port.Table('features', name='features')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        model = node_context.input['model']
        in_data = node_context.input['in-data']
        out_data = node_context.output['out-data']
        features = node_context.output['features']

        model.load()
        skl = model.get_skl()
        desc = model.get_desc()

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        kwargs['estimator'] = skl
        kwargs['prefit'] = True

        sfm = sklearn.feature_selection.SelectFromModel(**kwargs)
        X = table_to_array(in_data)
        Xsel = sfm.transform(X)
        indices = sfm.get_support(indices=True)
        x_names = desc.x_names
        if x_names is None:
            x_names = ["X{}".format(i) for i in X.shape[1]]
        array_to_table(np.array(x_names)[indices],
                       Xsel,
                       tbl=out_data)

        support = sfm.get_support()
        array_to_table(x_names,
                       support.reshape((1, len(support))),
                       tbl=features)
