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

import argparse
import fastr.execution.executionscript
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(description="Execute a job or network from commandline.")
    parser.add_argument('network', metavar='NETWORKFILE', type=str, help='File of the network to execute')
    return parser


def create_network_parser(network):
    parser = argparse.ArgumentParser(description="Execute the {} Network".format(network.id))
    for source in network.sourcelist:
        parser.add_argument('--{}'.format(source),
                            metavar=source.upper(),
                            required=True,
                            nargs='*',
                            help='Source data for {}'.format(source))

    for sink in network.sinklist:
        parser.add_argument('--{}'.format(sink),
                            metavar=sink.upper(),
                            required=True,
                            help='The Sink output specification for {}'.format(sink))
    return parser


def main():
    """
    Run a Network from the commandline
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args, unknown_args = parser.parse_known_args()

    network = fastr.api.Network.load(args.network)
    network_parser = create_network_parser(network._parent)
    network_args = vars(network_parser.parse_args(unknown_args))

    # Split data in Source and Sink data
    source_data = {}
    for source in network.sourcelist:
        source_data[source] = network_args[source]

    sink_data = {}
    for sink in network.sinklist:
        sink_data[sink] = network_args[sink]

    fastr.log.info('Source data: {}'.format(source_data))
    fastr.log.info('Sink data: {}'.format(sink_data))

    network.execute(source_data, sink_data)


if __name__ == '__main__':
    main()
