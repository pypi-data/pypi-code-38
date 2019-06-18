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
import sys
import os
import imp
import io

FASTR_LOG_TYPE = 'none'  # Do not get info about fastr

import fastr
from fastr.core.tool import Tool
from fastr.core.version import Version
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(
        description="Extract basic information from argparse."
    )
    parser.add_argument('infile', metavar='SCRIPT.py', help='Python script to inspect')
    parser.add_argument('outfile', metavar='TOOL.xml', help='created Tool stub')
    return parser


def cardinality_from_nargs(value):
    val_mapping = {'+': '1-*',
                   '?': '0-1',
                   '*': '0-*',
                   None: 1}

    if isinstance(value, int):
        return value
    else:
        return val_mapping[value]


def datatype_from_type(type_, metavar):
    type_mapping = {int: 'Int',
                    float: 'Float',
                    bool: 'Boolean',
                    str: 'String',
                    None: 'String'}
    if type_ in (None, str) and isinstance(metavar, str):
        return fastr.types.guess_type(metavar.lower(), exists=False).id
    else:
        if type_ in (None, str) and metavar is not None:
            type_ = type(metavar)
        return type_mapping.get(type_, 'AnyType')


def main():
    """
    Create a stub for a Tool based on a python script using argparse
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    # Extract arguments
    filepath = args.infile
    output_path = args.outfile

    # Extract argparse from desired script
    parser, stdout = extract_argparser(filepath)
    parser.prog = os.path.basename(filepath)

    description = parser.description
    if description is None:
        description = 'auto generated tool from {}'.format(filepath)

    tool = Tool()
    tool.id = os.path.splitext(os.path.basename(filepath))[0]
    tool.name = tool.id
    tool.version = Version('1.0')
    tool.filename = output_path
    tool.node_class = 'NodeRun'
    tool.command = {'authors': [],
                    'description': description,
                    'targets': [{'os': '*',
                                 'arch': '*',
                                 'bin': os.path.basename(filepath),
                                 'interpreter': 'python',
                                 'location': fastr.vfs.path_to_url(os.path.dirname(filepath)),
                                 'module': None}],
                    'url': 'http://www.bigr.nl/fastr',
                    'version': Version('1.0'),
                    'license': 'UNKNOWN'}
    tool.help = parser.format_help()

    tool.authors = [{'name': 'extract_argparse.py',
                     'email': 'jsmith@example.org',
                     'url': 'http://example.org'}]
    tool.description = description
    tool.tests = []

    inputs = []

    for option in parser._optionals._group_actions:
        prefix = max(option.option_strings, key=len)
        id_ = prefix.strip('-')
        param = {'id': id_,
                 'name': id_,
                 'prefix': prefix,
                 'description': option.help,
                 'cardinality': cardinality_from_nargs(option.nargs),
                 'required': option.required,
                 'repeat_prefix': False}

        if option.const is not None:
            param['datatype'] = datatype_from_type(option.type, option.const)
        elif option.choices is not None:
            param['enum'] = [str(x) for x in option.choices]
        else:
            param['datatype'] = datatype_from_type(option.type, option.metavar)

        inputs.append(param)

    tool.interface = fastr.plugins.FastrInterface(id_='{}_{}_interface'.format(tool.id, tool.command_version),
                                                  document={
                                                      'inputs': inputs,
                                                      'outputs': [],
                                                  })

    if os.path.isdir(output_path):
        output_path = os.path.join(output_path,
                                   tool.id + '.xml')
    with open(output_path, 'w') as output_fh:
        output_fh.write(tool.dumps('xml'))
    print('Written Tool stub to {}...'.format(output_path))


def extract_argparser(filepath):
    name = os.path.splitext(os.path.basename(filepath))[0]
    mod = imp.load_source(name, filepath)
    if not hasattr(mod, 'main'):
        print('Module does not have a main() function')
        return

    return find_argparser(mod.main, filepath)


def find_argparser(entry, basename=sys.argv[0]):
    # Catch stdout to string (no auto-print)
    old_stdout = sys.stdout
    temp_buffer = io.StringIO()
    sys.stdout = temp_buffer

    try:
        # Call entry with --help to trigger help and SystemExit by argparse
        sys.argv = [basename, '--help']
        entry()
    except SystemExit:
        # Follow traceback frames until we find the first ArgumentParser object
        tb = sys.exc_info()[2]
        tb_stack = [tb]
        while tb.tb_next is not None:
            tb = tb.tb_next
            tb_stack.append(tb)
        for tb in tb_stack:
            for name, obj in tb.tb_frame.f_locals.items():
                if isinstance(obj, argparse.ArgumentParser):
                    return obj, temp_buffer.getvalue()
        raise
    finally:
        # Cleanup StringIO and reset stdout
        sys.stdout = old_stdout
        temp_buffer.close()


if __name__ == '__main__':
    main()

