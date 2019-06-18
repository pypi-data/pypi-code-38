#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fastr

IS_TEST = False  # Do not use as a test


def create_network():
    network = fastr.Network(id="test_elastix_nipype_demo")

    source1 = network.create_source('ITKImageFile', id='fixed_img')
    source2 = network.create_source('ITKImageFile', id='moving_img')
    param1 = network.create_source('ElastixParameterFile', id='param_file')

    elastix_node = network.create_node('NipypeElastix', id='elastix')
    elastix_node.inputs['fixed_image'] = source1.output
    elastix_node.inputs['moving_image'] = source2.output
    link_param = network.create_link(param1.output, elastix_node.inputs['parameters'])
    link_param.converge = 0

    outtrans = network.create_sink('ElastixTransformFile', id='sink_trans')
    outtrans.inputs['input'] = elastix_node.outputs['transform']

    transformix_node = network.create_node('Transformix', id='transformix')
    transformix_node.inputs['image'] = source2.output
    transformix_node.inputs['transform'] = elastix_node.outputs['transform'][-1]

    outimage = network.create_sink('ITKImageFile', id='sink_image')
    outimage.inputs['input'] = transformix_node.outputs['image']

    network.draw_network(img_format='svg')
    network.dumpf('{}.json'.format(network.id), indent=2)

    return network


def source_data(network):
    return {'fixed_img': {'s1': 'vfs://example_tools/elastix_test/img0/slice047.mhd'},
            'moving_img': {'s1': 'vfs://example_tools/elastix_test/img1/slice091.mhd'},
            'param_file': ['vfs://example_tools/elastix_test/parAslice.txt',
                           'vfs://example_tools/elastix_test/parBslice.txt']}


def sink_data(network):
    return {'sink_trans': 'vfs://tmp/results/elastix_output_trans_{sample_id}_{cardinality}.txt',
            'sink_image': 'vfs://tmp/results/elastix_output_image_{sample_id}.nii.gz'}


def main():
    network = create_network()

    # Execute
    network.draw_network()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
