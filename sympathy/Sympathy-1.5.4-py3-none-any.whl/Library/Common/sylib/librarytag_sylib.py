# -*- coding:utf-8 -*-
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
from sympathy.api.nodeconfig import LibraryTags, TagType, GroupTagType


class SylibLibraryTags(LibraryTags):
    class_tags = (
        GroupTagType(
            'Root',
            # Input group.
            [GroupTagType(
                'Input',
                [TagType('Import',
                         'Import external data from files or databases'),
                 TagType('Generate',
                         'Generate data')]),

             # Export group.
             GroupTagType(
                'Output',
                [TagType('Export',
                         'Export data to external files or databases')]),

             # Data Processing.
             GroupTagType(
                'DataProcessing',
                [TagType('Calculate',
                         'Calculate data based on input'),
                 TagType('Convert',
                         'Convert between internal datatypes'),
                 TagType('List',
                         'List data operations'),
                 TagType('Tuple',
                         'Tuple data operations'),
                 TagType('Text',
                         'Text data operations'),
                 TagType('Index',
                         'Index data operations'),
                 TagType('Select',
                         'Select data parts'),
                 TagType('TransformStructure',
                         'Transform structure',
                         name='Structure'),
                 TagType('TransformData',
                         'Transform data',
                         name='Data'),
                 TagType('TransformMeta',
                         'Transform meta',
                         name='Attributes')],

                name='Data Processing'),

             # Visual group.
             GroupTagType(
                 'Visual',
                 [TagType('Figure',
                          'Figure operations'),
                  TagType('Plot',
                          'Plot operations'),
                  TagType('Report',
                          'Report generating operations')]),

             # Analysis group.
             GroupTagType(
                 'Analysis',
                 [TagType('Statistic',
                          'Statistical data operations',
                          name='Statistics'),
                  TagType('SignalProcessing',
                          'Signal processing data operations',
                          name='Signal Processing'),
                  TagType('Features',
                          'Features')]),

             # Disk group.
             GroupTagType(
                'Disk',
                [TagType('File',
                         'File processing data operations')]),

             # Generic group.
             GroupTagType(
                 'Generic',
                 [TagType('Lambda',
                          'Operations for lambda functions'),
                  TagType('Control',
                          'Control flow'),
                  TagType('Configuration',
                          'Nodes for working with node configurations'),
                  TagType('List',
                          'List data operations'),
                  TagType('Tuple',
                          'Tuple data operations')]),

             # Example group.
             GroupTagType(
                 'Example',
                 [TagType('NodeWriting',
                          'Example nodes demonstrating different aspects of '
                          'node writing',
                          name='Node writing'),
                  TagType('Legacy',
                          'Example nodes from before Sympathy 1.0'),
                  TagType('Misc',
                          'Miscellaneous examples')]),

             # Development group.
             GroupTagType(
                 'Development',
                 [TagType('Example',
                          'Example nodes demonstrating different aspects of '
                          'node writing',
                          name='Example'),
                  TagType('Test',
                          'Test nodes for validating data'),
                  TagType('Debug',
                          'Test nodes for debugging')]),

             # Image processing
             GroupTagType('ImageProcessing',
                          [TagType('IO',
                                   'Image source, generators and exporters',
                                   name='Input/Output'),
                           TagType('Layers', 'Operations on image layers',
                                   name='Layer operations'),
                           TagType('Segmentation', 'Segmentation, label and masks',
                                   name='Segmentation'),
                           TagType('ImageManipulation',
                                   'Operations on images yielding new images',
                                   name='Image Manipulation'),
                           TagType('Extract',
                                   'Extracts statistical data from images',
                                   name='Extract statistics'),
                           TagType('Other', 'Other image processing')],
                          name="Image processing"),

             # Machine learning
             GroupTagType(
                 'MachineLearning',
                 [TagType('Supervised',
                          'Supervised machine learning algorithms'),
                  TagType('Unsupervised',
                          'Unsupervised machine learning algorithms'),
                  TagType('Regression',
                          'Nummerical regression'),
                  TagType('Analysis',
                          'Analysis'),
                  TagType('Clustering',
                          'Creates and labels clusters of data'),
                  TagType('Processing',
                          'Data (pre)-processing algorithms'),
                  TagType('Partitioning',
                          'Data partitioning and cross-validation',
                          name='Partitioning and validation'),
                  TagType('HyperParameters',
                          'Parameter search',
                          name='Parameters'),
                  TagType('Apply',
                          'Applies a model to some data, eg. fitting a model, '
                          'predicting, or transforming data',
                          name='Apply model'),
                  TagType('Metrics',
                          'Computes metrix from a fitted model and dataset',
                          name='Metrics'),
                  TagType('IO',
                          'Methods for saving/loading models and '
                          'example datasets'),
                  TagType('DimensionalityReduction',
                          'Reduces number of dimensions of a dataset',
                          name='Dimensionality reduction'),
                  # Tab disbled for release 1.4.3, aiming for 1.4.4 instead
                  # TagType('Tensors',
                  #         'Tensor based neural networks'),
                  ],
                 name='Machine Learning'),

             # Hidden group.
             GroupTagType(
                 'Hidden',
                 [TagType('Deprecated',
                          'Deprecated nodes (will be removed)'),
                  TagType('Experimental',
                          'Experimental nodes'),
                  TagType('Replaced',
                          'Node has been replaced with new node with '
                          'different interface'),
                  TagType('Internal',
                          'Nodes that are only used internally by the '
                          'Sympathy platform'),
                  TagType('Egg',
                          'Easter egg nodes')])]))

    def __init__(self):
        super(SylibLibraryTags, self).__init__()
        self._root = self.class_tags
