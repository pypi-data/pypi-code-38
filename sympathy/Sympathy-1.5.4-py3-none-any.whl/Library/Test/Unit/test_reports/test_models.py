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
import unittest
import copy
from sylib.report import models


class TestModels(unittest.TestCase):
    def setUp(self):
        self.data = {
            'type': 'root',
            'version': 1,
            'data': [],
            'scales': [
                {
                    'id': 'x-scale',
                    'type': 'Linear',
                    'domain': [-10, 10],
                    'range': [-10, 10]
                },
                {
                    'id': ' y-scale',
                    'type': 'Linear',
                    'domain': [-10, 10],
                    'range': [-10, 10]
                }
            ],
            'pages': [
                {
                    'type': 'page',
                    'title': 'Page1',
                    'content': [{
                        'type': 'layout',
                        'kind': 'vertical',
                        'items': [
                            {
                                'type': 'graph',
                                'id': 'graph1',
                                'title': 'Graph',
                                'width': 500,
                                'height': 500,
                                'grid': False,
                                'projection': 'Cartesian',
                                'dimensions': [
                                    [
                                        {
                                            'id': 'x-axis',
                                            'title': 'x-axis',
                                            'scale': 'x-scale'
                                        }
                                    ],
                                    [
                                        {
                                            'id': 'y-axis',
                                            'title': 'y-axis',
                                            'scale': 'y-scale'
                                        }
                                    ]
                                ],
                                'layers': [
                                    {
                                        'type': 'scatter',
                                        'data': [
                                            {
                                                'source': 'data1',
                                                'axis': 'x-axis'
                                            },
                                            {
                                                'source': 'data2',
                                                'axis': 'y-axis'
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                'type': 'layout',
                                'kind': 'horizontal',
                                'items': [
                                    {
                                        'type': 'graph',
                                        'id': 'graph2',
                                        'title': 'Graph',
                                        'width': 500,
                                        'height': 500,
                                        'grid': False,
                                        'projection': 'Cartesian',
                                        'dimensions': [
                                            [
                                                {
                                                    'id': 'x-axis',
                                                    'title': 'x-axis',
                                                    'scale': 'x-scale'
                                                }
                                            ],
                                            [
                                                {
                                                    'id': 'y-axis',
                                                    'title': 'y-axis',
                                                    'scale': 'y-scale'
                                                }
                                            ]
                                        ],
                                        'layers': [
                                            {
                                                'type': 'scatter',
                                                'data': [
                                                    {
                                                        'source': 'data1',
                                                        'axis': 'x-axis'
                                                    },
                                                    {
                                                        'source': 'data2',
                                                        'axis': 'y-axis'
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }]
                }
            ]
        }

        self.model = models.Root(self.data)

    def test_remove_node(self):
        node = self.model.find_node(models.Graph, 'graph1')
        parent = node.parent
        self.assertEqual(len(parent.data['items']), 2)

        models.remove_node(node)

        # Object structure.
        self.assertIsNone(self.model.find_node(models.Graph, 'graph1'))
        self.assertEqual(parent.row_count(), 1)
        # Dictionary structure.
        self.assertEqual(len(parent.data['items']), 1)

    def test_insert_node(self):
        node = self.model.find_node(models.Graph, 'graph1')
        parent = node.parent
        child_list = copy.copy(parent.data['items'])
        child_list.reverse()

        models.remove_node(node)
        models.insert_node(node, parent, 1)

        # Object structure.
        self.assertIsNotNone(self.model.find_node(models.Graph, 'graph1'))
        self.assertNotEqual(parent.child(0), node)
        self.assertEqual(parent.child(1), node)
        # Dictionary structure.
        self.assertEqual(len(parent.data['items']), 2)
        self.assertListEqual(parent.data['items'], child_list)

    def test_move_node(self):
        node = self.model.find_node(models.Graph, 'graph1')
        parent = node.parent
        child_list = copy.copy(parent.data['items'])
        child_list.reverse()

        models.move_node(node, parent, 1)

        # Object structure.
        self.assertIsNotNone(self.model.find_node(models.Graph, 'graph1'))
        self.assertNotEqual(parent.child(0), node)
        self.assertEqual(parent.child(1), node)
        # Dictionary structure.
        self.assertEqual(len(parent.data['items']), 2)
        self.assertListEqual(parent.data['items'], child_list)
