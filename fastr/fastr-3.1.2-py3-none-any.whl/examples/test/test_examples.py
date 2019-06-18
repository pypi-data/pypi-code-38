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

import os
import imp

import pytest

import fastr

EXAMPLE_LIST = [
    'source_sink',
    'collapse',
    'expand',
    'collapse_expand',
    'filecopy',
    'add_ints',
    'shift_links',
    'auto_prefix',
    'chunk_test',
    'input_groups',
    'failing_network',
    'advanced_linking',
    'macro_node',
    'macro_node2',
    'failing_macro',
]


@pytest.mark.parametrize("example_name", EXAMPLE_LIST)
@pytest.mark.slow
def test_examples(example_name, tmpdir_factory):
    # Set some config variables
    example_path = os.path.join(fastr.config.examplesdir, example_name + '.py')
    example_module = imp.load_source(example_name, example_path)
    network = example_module.create_network().parent

    reference_dir = os.path.join(os.path.dirname(example_path),
                                 'data',
                                 'reference',
                                 '{}_{}'.format(network.id, network.version))

    fastr.log.info('Using reference dir: {}'.format(reference_dir))
    if os.path.isdir(reference_dir):
        result = network.test(reference_dir, network)
        if result:
            for error in result:
                print(error)
        assert(len(result) == 0)
    else:
        raise ValueError('Could not find reference data for test!')

