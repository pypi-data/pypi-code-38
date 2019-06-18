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

import imp
import os
import shutil

import fastr
from fastr.examples.test.test_examples import EXAMPLE_LIST


def create_reference(example):
    examples_dir = fastr.config.examplesdir
    example_path = os.path.abspath(os.path.join(examples_dir, example + '.py'))
    example_module = imp.load_source(example, example_path)

    network = example_module.create_network()
    output_directory = './data/reference/{n.id}_{n.version}'.format(n=network)

    if os.path.exists(output_directory):
        fastr.log.info('Skipping creation of {}, already exists!'.format(output_directory))
        return

    # Do not publish this to PIM
    fastr.config.pim_host = ''  # Do not publish anything to PIM

    source_data = example_module.source_data(network)
    network.create_reference(source_data=source_data, output_directory=output_directory)
    shutil.rmtree(os.path.join(output_directory, '__fastr_run_tmp__'))


def generate_all_references():
    for example in EXAMPLE_LIST:
        create_reference(example)


if __name__ == '__main__':
    generate_all_references()
