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
from fastr.utils.cmd import add_parser_doc_link
FASTR_LOG_TYPE = 'none'  # Do not get info about fastr


def get_parser():
    parser = argparse.ArgumentParser(
        description="Verify fastr resources, at the moment only tool definitions"
                    "are supported."
    )
    parser.add_argument('resource_type', metavar='TYPE', choices=['tool'],
                        help='Type of resource to verify (e.g. tool)')
    parser.add_argument('path', help='path of the resource to verify')
    return parser


def main():
    """
    Verify fastr resources, at the moment only tool definitions are supported.
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    import fastr
    from fastr.utils.verify import verify_tool

    resource_type = args.resource_type.lower()
    if resource_type == 'tool':
        verify_tool(args.path)
    else:
        fastr.log.error('Unknown resource type {}'.format(resource_type))
