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
import os

from fastr.core import provenance

import fastr
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(
        description="Export the provenance information from JSON to other formats"
                    " or plot the provenance data as a graph.")
    parser.add_argument('result', metavar='RESULTFILE', nargs='?', type=str, help='File of the job to execute (default ./__fastr_prov__.json)')
    parser.add_argument('-so', '--syntax-out-file', type=str, help="Write the syntax to file.")
    parser.add_argument('-sf', '--syntax-format', default='json', type=str, help="Choices are: [json], provn or xml")
    parser.add_argument('-i', '--indent', type=int, default=2, help="Indent size of the serialized documents.")
    parser.add_argument('-vo', '--visualize-out-file', type=str, help="Visualize the provenance. The most preferred format is svg. You can specify any format pydot supports. Specify the format by postfixing the filename with an extension.")
    return parser


def get_prov_document(result):
    return provenance.prov.read(result, 'json')


def main():
    """
    Get PROV information from the result pickle.
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    if args.result is not None:
        result = args.result
    else:
        curdir_contents = os.listdir('.')
        if '__fastr_prov__.json' in curdir_contents:
            result = '__fastr_prov__.json'
        else:
            fastr.log.critical('No result given and cannot find __fastr_result__.pickle.gz in current directory!')
            exit()

    # Get the prov document.
    provenance = get_prov_document(result)
    syntax_format = args.syntax_format

    if args.syntax_out_file:
        provenance.serialize(destination=args.syntax_out_file, format=syntax_format)
        fastr.log.info("Written the provenance syntax in {} format to: {}".format(syntax_format, args.syntax_out_file))

    if args.visualize_out_file:
        provenance.plot(args.visualize_out_file, show_element_attributes=False, show_relation_attributes=False)
        fastr.log.info("Vizualized the provenance in: {}".format(args.visualize_out_file))

    if not args.visualize_out_file and not args.syntax_out_file:
        # There is no output file give so let the serializer print to stdout.
        print(provenance.serialize(format=syntax_format, indent=2))


if __name__ == '__main__':
    main()
