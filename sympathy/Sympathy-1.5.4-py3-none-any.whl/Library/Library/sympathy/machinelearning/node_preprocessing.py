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
import sklearn.preprocessing

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.preprocessing import StandardScalerDescriptor
from sylib.machinelearning.preprocessing import RobustScalerDescriptor
from sylib.machinelearning.preprocessing import MaxAbsScalerDescriptor
from sylib.machinelearning.preprocessing import OneHotEncoderDescriptor
from sylib.machinelearning.preprocessing import PolynomialFeaturesDescriptor
from sylib.machinelearning.preprocessing import LabelBinarizerDescriptor
from sylib.machinelearning.preprocessing import CategoryEncoderDescriptor
from sylib.machinelearning.preprocessing import CategoryEncoder
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y

from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolListType
from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatListType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class StandardScaler(SyML_abstract, node.Node):
    name = 'Standard Scaler'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Standardize features by removing the mean and scaling to unit variance.

Centering and scaling happen independently on each feature by
computing the relevant statistics on the samples in the training
set. Mean and standard deviation are then stored to be used on later
data using the transform method.  Standardization of a dataset is a
common requirement for many machine learning estimators: they might
behave badly if the individual feature do not more or less look like
standard normally distributed data (e.g. Gaussian with 0 mean and unit
variance)."""
    nodeid = 'org.sysess.sympathy.machinelearning.standard_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = StandardScalerDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'with_mean',
         'type': BoolType(default=True)},
        {'name': 'with_std',
         'type': BoolType(default=True)},
    ], doc_class=sklearn.preprocessing.StandardScaler)
    descriptor.set_mirroring()
    descriptor.set_attributes([
        {'name': 'scale_', 'cnames': names_from_x},
        {'name': 'mean_', 'cnames': names_from_x},
        {'name': 'var_', 'cnames': names_from_x},
        {'name': 'n_samples_seen_'},
    ], doc_class=sklearn.preprocessing.StandardScaler)

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
        skl = sklearn.preprocessing.StandardScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class RobustScaler(SyML_abstract, node.Node):
    name = 'Robust Scaler'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Scale features using statistics that are robust to outliers.

This Scaler removes the median and scales the data according to the
quantile range (defaults to IQR: Interquartile Range). The IQR is the
range between the 1st quartile (25th quantile) and the 3rd quartile
(75th quantile). Centering and scaling happen independently on each
feature (or each sample, depending on the axis argument) by computing
the relevant statistics on the samples in the training set. Median and
interquartile range are then stored to be used on later data using the
transform method. Standardization of a dataset is a common requirement
for many machine learning estimators. Typically this is done by
removing the mean and scaling to unit variance. However, outliers can
often influence the sample mean / variance in a negative way. In such
cases, the median and the interquartile range often give better
results.  """
    nodeid = 'org.sysess.sympathy.machinelearning.robust_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = RobustScalerDescriptor()
    descriptor.name = name
    descriptor.set_mirroring()
    descriptor.set_info([
        {
            'name': 'with_centering',
            'type': BoolType(default=True)
        },
        {
            'name': 'with_scaling',
            'type': BoolType(default=True)
        },
        {
            'name': 'quantile_range',
            'type': FloatListType(
                default=[25.0, 75.0], min_length=2, max_length=2,
                min_value=0.0, max_value=100.0
            )
        },
    ], doc_class=sklearn.preprocessing.RobustScaler)
    descriptor.set_attributes([
        {'name': 'center_', 'cnames': names_from_x},
        {'name': 'scale_', 'cnames': names_from_x},
    ], doc_class=sklearn.preprocessing.RobustScaler)

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
        skl = sklearn.preprocessing.RobustScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class MaxAbsScaler(SyML_abstract, node.Node):
    name = 'Max Abs Scaler'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Scale each feature by its maximum absolute value.

This estimator scales and translates each feature individually such
that the maximal absolute value of each feature in the training set
will be 1.0. It does not shift/center the data, and thus does not
destroy any sparsity.
"""
    nodeid = 'org.sysess.sympathy.machinelearning.maxabs_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = MaxAbsScalerDescriptor()
    descriptor.name = name
    descriptor.set_info([])
    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'scale_', 'cnames': names_from_x},
        {'name': 'max_abs_', 'cnames': names_from_x},
        {'name': 'n_samples_seen_'},
    ], doc_class=sklearn.preprocessing.MaxAbsScaler)

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
        skl = sklearn.preprocessing.MaxAbsScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class Normalizer(SyML_abstract, node.Node):
    name = 'Normalizer'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'normalizer.svg'
    description = """
Normalize samples individually to unit norm.

Each sample (i.e. each row of the data matrix) with at least one non
zero component is rescaled independently of other samples so that its
norm (l1, l2 or max) equals one."""
    nodeid = 'org.sysess.sympathy.machinelearning.normalizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {
            'name': 'norm',
            'type': StringSelectionType(
                options=['l1', 'l2', 'max'],
                default='l2')
        }
    ], doc_class=sklearn.preprocessing.Normalizer)
    descriptor.set_mirroring()

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
        skl = sklearn.preprocessing.Normalizer(**kwargs)

        model.set_skl(skl)
        model.save()


class Binarizer(SyML_abstract, node.Node):
    name = 'Binarizer'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'binarizer.svg'
    description = """
Binarize data (set feature values to 0 or 1) according to a threshold.

Values greater than the threshold map to 1, while values less than or
equal to the threshold map to 0. With the default threshold of 0, only
positive values map to 1. Binarization is a common operation on text
count data where the analyst can decide to only consider the presence
or absence of a feature rather than a quantified number of occurrences
for instance. It can also be used as a pre-processing step for
estimators that consider boolean random variables (e.g. modelled using
the Bernoulli distribution in a Bayesian setting)."""
    nodeid = 'org.sysess.sympathy.machinelearning.binarizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'threshold',
         'type': FloatType(default=0.0)}
    ], doc_class=sklearn.preprocessing.Binarizer)
    descriptor.set_mirroring()

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
        skl = sklearn.preprocessing.Binarizer(**kwargs)

        model.set_skl(skl)
        model.save()


class LabelBinarizer(SyML_abstract, node.Node):
    name = 'Label Binarizer'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'label_binarizer.svg'
    description = """
Binarize labels in a one-vs-all fashion.

Several regression and binary classification algorithms are available
in the scikit. A simple way to extend these algorithms to the
multi-class classification case is to use the so-called one-vs-all
scheme. At learning time, this simply consists in learning one
regressor or binary classifier per class. In doing so, one needs to
convert multi-class labels to binary labels (belong or does not belong
to the class). LabelBinarizer makes this process easy with the
transform method. At prediction time, one assigns the class for which
the corresponding model gave the greatest confidence. LabelBinarizer
makes this easy with the inverse_transform method """
    nodeid = 'org.sysess.sympathy.machinelearning.label_binarizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = LabelBinarizerDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'pos_label',
         'type': IntType(default=1)},
        {'name': 'neg_label',
         'type': IntType(default=0)},
    ], doc_class=sklearn.preprocessing.LabelBinarizer)
    descriptor.set_attributes([
        {'name': 'classes_', 'rnames': names_from_y},
        {'name': 'y_type_', },
    ], doc_class=sklearn.preprocessing.LabelBinarizer)

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
        skl = sklearn.preprocessing.LabelBinarizer(**kwargs)

        model.set_skl(skl)
        model.save()


class OneHotEncoder(SyML_abstract, node.Node):
    name = 'One-Hot Encoder'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'label_binarizer.svg'
    description = """
Encode categorical integer features using a one-hot aka one-of-K scheme.

For each categorical input feature, a number of output features will
be given of which exactly one is marked as true and the rest as
false. This encoding is needed for feeding categorical data to many
scikit-learn estimators, notably linear models and SVMs with the
standard kernels. Note: a one-hot encoding of y labels should use a
LabelBinarizer instead."""
    nodeid = 'org.sysess.sympathy.machinelearning.one_hot_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = OneHotEncoderDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'n_values',
         'type': UnionType([StringSelectionType(["auto"]),
                            IntType(min_value=0),
                            IntListType(min_length=1, min_value=0)],
                           default='auto')},
        {'name': 'categorical_features',
         'type': UnionType([
             StringSelectionType(["all"]),
             IntListType(min_length=1, min_value=0),
             BoolListType(min_length=1)], default='all')},
        {'name': 'handle_unknown',
         'desc': 'How to handle unknown categories during (non-fit) transform',
         'type': StringSelectionType(['error', 'ignore'])},
        {'name': 'sparse',
         'desc': """
Will generate sparse matrix if true.
Warning: sparse matrices are not handled by all Sympathy nodes and may be
silently converted to non-sparse arrays""",
         'type': BoolType(default=False)},
    ], doc_class=sklearn.preprocessing.OneHotEncoder)
    descriptor.set_attributes([
        {'name': 'active_features_'},
        {'name': 'feature_indices_', 'cnames': names_from_x},
        {'name': 'n_values_', 'cnames': names_from_x},
    ], doc_class=sklearn.preprocessing.OneHotEncoder)

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
        skl = sklearn.preprocessing.OneHotEncoder(**kwargs)

        model.set_skl(skl)
        model.save()


class Imputer(SyML_abstract, node.Node):
    name = 'Imputer'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'imputer.svg'
    description = (
        'Replaces missing values in a dataset with a computed value infered '
        'from the remained of the dataset.')
    nodeid = 'org.sysess.sympathy.machinelearning.imputer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'missing_values',
         'type': UnionType([
             StringSelectionType(["NaN"]),
             IntType()], default='NaN')},
        {'name': 'strategy',
         'type': StringSelectionType([
             "mean", "median", "most_frequent"], default="mean")},
        {'name': 'axis',
         'type': IntType(min_value=0, max_value=1, default=0)},
    ], doc_class=sklearn.preprocessing.Imputer)
    descriptor.set_mirroring()
    descriptor.set_attributes([
        {'name': 'statistics_', 'cnames': names_from_x},
    ], doc_class=sklearn.preprocessing.Imputer)

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
        skl = sklearn.preprocessing.Imputer(**kwargs)

        model.set_skl(skl)
        model.save()


class PolynomialFeatures(SyML_abstract, node.Node):
    name = 'Polynomial Features'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'polynomial.svg'
    description = (
        'Generate a new feature matrix consisting of all polynomial '
        'combinations of the features with less than a given degree')
    nodeid = 'org.sysess.sympathy.machinelearning.polynomial_features'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = PolynomialFeaturesDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'degree',
         'type': IntType(min_value=0, default=2)},
        {'name': 'interaction_only',
         'type': BoolType(default=False)},
        {'name': 'include_bias',
         'type': BoolType(default=True)},
    ], doc_class=sklearn.preprocessing.PolynomialFeatures)
    descriptor.set_attributes([
        {'name': 'n_input_features_', },
        {'name': 'n_output_features_', },
        {'name': 'powers_', 'cnames': names_from_x, 'rnames': names_from_y},
    ], doc_class=sklearn.preprocessing.PolynomialFeatures)

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
        skl = sklearn.preprocessing.PolynomialFeatures(**kwargs)

        model.set_skl(skl)
        model.save()


class LabelEncoder(SyML_abstract, node.Node):
    name = 'Label Encoder'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'label_encoder.svg'
    description = (
        'Encode single string labels with value between 0 and n_classes-1.')
    nodeid = 'org.sysess.sympathy.machinelearning.label_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    descriptor.set_info([
    ])
    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'classes_'},
    ], doc_class=sklearn.preprocessing.LabelEncoder)

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
        skl = sklearn.preprocessing.LabelEncoder(**kwargs)

        model.set_skl(skl)
        model.save()


class CategoryEncoderNode(SyML_abstract, node.Node):
    name = 'Categorical Encoder'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'categorical_encoder.svg'
    description = (
        'Encodes all inputs into integer features, assumes '
        'that all inputs are Categorical ')
    nodeid = 'org.sysess.sympathy.machinelearning.category_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = CategoryEncoderDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'max_categories',
         'type': UnionType([NoneType(), IntType(min_value=1)], default=None),
         'desc': (
             'Maximum number of categories for any feature. '
             'Remaining values are encoded as 0. '
             'If None then no upper bound on number of features')},
    ])
    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'categories_',
         'desc': (
             'List of dictionaries that map each input feature into '
             'a categorical integer')},
        {'name': 'inv_categories_',
         'desc': (
             'List of dictionaries that map each output value into '
             'an corresponding input value')}
        ])

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
        skl = CategoryEncoder(**kwargs)

        model.set_skl(skl)
        model.save()
