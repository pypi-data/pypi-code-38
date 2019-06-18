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
from collections import namedtuple
from copy import deepcopy

import fastr
from fastr import exceptions
from fastr.core.version import Version
from fastr.utils.cmd import add_parser_doc_link
FASTR_LOG_TYPE = 'none'  # Do not get info about fastr


class dummy_container:
    def __getitem__(self, value):
        return value


FastrNamespaceType = namedtuple('FastrNamespaceType', ['toollist', 'typelist'])


EVAL_GLOBALS = {
    'fastr': FastrNamespaceType(dummy_container(), dummy_container()),
    'toollist': dummy_container(),
    'typelist': dummy_container(),
}


def get_parser():
    parser = argparse.ArgumentParser(
        description=("Upgrades a python file that creates a Network to the new"
                     " fastr 3.x syntax. The file will be parsed and the"
                     " full syntax tree will be transformed to fit the new"
                     " syntax."
                     "\n\n.. note:: Solves most common problems, but cannot always solve 100% of the issues")
    )
    parser.add_argument('infile', metavar='NETWORK.py', help='Network creation file (in python) to upgrade')
    parser.add_argument('outfile', metavar='NEW.py', help='location of the result file')
    parser.add_argument('--type', metavar='TYPE', help='tool of resource to upgrade, one of: network, tool')
    return parser


def find_tool(toolspec):
    if isinstance(toolspec, str):
        namespace = None
        toolname = toolspec
        version = None
    elif isinstance(toolspec, tuple):
        if len(toolspec) == 2:
            toolname, version = toolspec
            namespace = None
        elif len(toolspec) == 3:
            namespace, toolname, version = toolspec
        else:
            raise exceptions.FastrToolUnknownError(f'Cannot use illegal tool spec {toolspec} with len {len(toolspec)}')
    else:
        raise exceptions.FastrToolUnknownError(
            f'Invalid toolspec {toolspec} type to find a tool, must be str or tuple, got a {type(toolspec).__name__}'
        )

    if version is None and '/' in toolname:
        toolname, version = toolname.split('/', 1)

    if namespace is None and '.' in toolname:
        namespace, toolname = toolname.rsplit('.', 1)

    if isinstance(version, str):
        version = Version(version)

    if namespace:
        namespace = '/'.join(namespace.split('.'))

    matching_tools = [t for t in fastr.tools.values() if t._id == toolname and
                      (version is None or t.command_version == version) and
                      (namespace is None or t.namespace == namespace)]

    if not matching_tools:
        raise exceptions.FastrToolUnknownError('Could not find tool: {}/{}:{}'.format(
            namespace or '$NAMESPACE',
            toolname,
            version or '$VERSION'
        ))

    matching_tools.sort(key=lambda x: (x.command_version, x.version), reverse=True)

    return matching_tools[0]


def upgrade_network(infile, outfile):
    try:
        from redbaron import RedBaron
    except ImportError:
        print("The upgrade command needs the redbaron package which is currently not installed. "
              "Please install the package.\n\nExample using pip:\n  $ pip install redbaron")
        return

    fastr.log.info('Loading input file...')
    with open(infile, 'r') as file_handle:
        code_file = RedBaron(file_handle.read())

    # Add import of resourcelimit
    fastr.log.info('Adding ResourceLimit import')
    for node in code_file.find_all('ImportNode', value=lambda x: x.dumps() == 'fastr'):
        node.insert_after('from fastr.api import ResourceLimit')

    # Replace all fastr.Network by fastr.create_network
    fastr.log.info('Updating network creation...')
    matches = code_file.find_all('AtomtrailersNode', value=lambda x: x.dumps().startswith('fastr.Network'))
    network_id = None
    for match in matches:
        if match.value[1].value != 'Network':
            continue

        match.value[1] = 'create_network'

        # Save the network id for later use
        for nr, subnode in enumerate(match.value[2]):
            if (subnode.target is None and nr == 0) or subnode.target.value == 'id_':
                try:
                    network_id = eval(subnode.value.dumps(), EVAL_GLOBALS, {})
                except:
                    network_id = subnode.value.dumps()

    # Change arguments for functions
    fastr.log.info('Updating method arguments...')
    for arg in code_file.find_all('CallArgumentNode'):
        if arg.target and arg.target.value == 'id_':
            arg.target.value = 'id'

        if arg.target and arg.target.value in ['nodegroup', 'sourcegroup']:
            arg.target.value = 'node_group'

        if arg.target and arg.target.value in ['stepid']:
            arg.target.value = 'step_id'

    # Add tool version and update tool name
    fastr.log.info('Updating create_node to include more version info...')
    for node in code_file.find_all('CallNode'):
        # Skip elements which do not call anything?
        if node.previous is None:
            continue

        if node.previous.value in ['create_source', 'create_constant', 'create_sink']:
            fastr.log.info(f'Updating {node.previous.value} statement: {node.parent}')
            if str(node.value[0].target) == 'datatype':
                node.value[0].target = ''

            try:
                data_type = eval(node.value[0].value.dumps(), EVAL_GLOBALS, {})
            except Exception:
                data_type = node.value[0].value

            node.value[0].value = f"'{data_type}'"

        elif node.previous.value == 'create_node':
            fastr.log.info(f'Updating create_node statement: {node.parent}')

            if str(node.value[0].target) == 'tool':
                node.value[0].target = ''

            tool_def = node.value[0].value.dumps()
            try:
                tool = eval(tool_def, EVAL_GLOBALS, {})
                tool = find_tool(tool)
                tool_version = tool.version
                tool_spec = tool.ns_id
                fastr.log.info(f'Found tool {tool}')
            except:
                fastr.log.error(f'Could not find tool based on: {tool_def}, using {tool_def} with tool_version="unknown"')
                tool_spec = tool_def
                tool_version = 'unknown'

            node.value[0].value = f"'{tool_spec}'"
            full_syntax = node.fst()
            if len(full_syntax['value']) < 3:
                raise ValueError('Cannot understand indentation of:\n{}'.format(node))

            # Get comma spec
            if len(full_syntax['value']) < 4:
                comma = deepcopy(full_syntax['value'][1])
            else:
                comma = deepcopy(full_syntax['value'][3])

            # Get call argument spec
            if not full_syntax['value'][2]['target']:
                full_syntax['value'][2]['target'] = {'type': 'name', 'value': 'id'}
            extra_arg = deepcopy(full_syntax['value'][2])

            if comma['type'] != 'comma' or extra_arg['type'] != 'call_argument':
                raise ValueError('Cannot understand syntax of:\n{}'.format(node))

            # Adapt call spec to correct values
            extra_arg['target']['value'] = 'tool_version'
            extra_arg['value']['value'] = f"'{tool_version}'"
            extra_arg['target']['type'] = 'name'

            # Insert and rebuild
            full_syntax['value'].insert(2, extra_arg)
            full_syntax['value'].insert(3, comma)
            node.replace(node.from_fst(full_syntax))

            # Get resource limits
            args = []
            to_remove = []
            for subnode in node.value:
                if subnode.target is not None and subnode.target.value == 'cores':
                    args.append(f'cores={subnode.value}')
                    to_remove.append(subnode)

                if subnode.target is not None and subnode.target.value == 'memory':
                    args.append(f'memory={subnode.value}')
                    to_remove.append(subnode)

                if subnode.target is not None and subnode.target.value == 'walltime':
                    args.append(f'time={subnode.value}')
                    to_remove.append(subnode)

            for subnode in to_remove:
                node.remove(subnode)

            if len(args) > 0:
                node.value.append('resources=ResourceLimit({})'.format(', '.join(args)))

    # Update draw_network -> draw and all argument changes
    fastr.log.info('Updating network draw to to new syntax...')
    for node in code_file.find_all('CallNode'):
        if node.previous.value != 'draw_network':
            continue

        node.previous.value = 'draw'

        name = network_id
        parsed_name = True
        img_format = 'svg'
        parsed_img_format = True
        file_path_node = None
        img_format_node = None
        for nr, subnode in enumerate(node.value):
            if (subnode.target is None and nr == 0) or (subnode.target is not None and subnode.target.value == 'name'):
                try:
                    name = eval(subnode.value.dumps(), EVAL_GLOBALS, {})
                except Exception:
                    name = subnode.value.dumps()
                    parsed_name = False

                file_path_node = subnode

            if (subnode.target is None and nr == 1) or (subnode.target is not None and subnode.target.value == 'img_format'):
                try:
                    img_format = eval(subnode.value.dumps(), EVAL_GLOBALS, {})
                except Exception:
                    img_format = subnode.value.dumps()
                    parsed_img_format = False

                img_format_node = subnode

            if (subnode.target is None and nr == 2) or (subnode.target is not None and subnode.target.value == 'draw_dimension'):
                subnode.target = 'draw_dimensions'

            if (subnode.target is None and nr == 3) or (subnode.target is not None and subnode.target.value == 'expand_macro'):
                subnode.target = 'expand_macros'

        # Construct correct file_path value
        if parsed_name and parsed_img_format:
            file_path_value = "'{}.{}'"
        elif parsed_name and not parsed_img_format:
            file_path_value = "'{}.' + {}"
        elif not parsed_name and parsed_img_format:
            file_path_value = "{} + '.{}'"
        else:
            file_path_value = "{} + '.' + {}"

        file_path_value = file_path_value.format(name, img_format)

        # Replace name and format arguments with the file_path argument
        if file_path_node is not None:
            file_path_node.replace("file_path={}".format(file_path_value))

        if img_format_node is not None:
            if file_path_node is not None:
                index = node.index_on_parent

                full_syntax = node.fst()
                full_syntax['value'].pop(node.index_on_parent)
                if len(full_syntax['value']) > index:
                    full_syntax['value'].pop(node.index_on_parent)

                node.replace(node.from_fst(full_syntax))
            else:
                img_format_node.replace("file_path={}".format(file_path_value))

    fastr.log.info('Writing output file...')
    with open(outfile, 'w') as output_file_handle:
        output_file_handle.write(code_file.dumps())


def upgrade_tool(infile, outfile):
    from fastr.core.tool import Tool

    fastr.log.info(f'Loading tool definition from {infile}')
    tool = Tool.loadf(infile)
    fastr.log.info(f'Saving new tool definition to {outfile}')
    tool.dumpf(outfile, method='yaml')


def main():
    """
    Upgrade a fastr 2.x python file to fastr 3.x syntax
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    input_file = args.infile
    output_file = args.outfile
    resource_type = args.type

    if resource_type is None:
        if input_file.endswith('.py'):
            resource_type = 'network'
        elif input_file.endswith('.xml'):
            resource_type = 'tool'

    if resource_type == 'network':
        try:
            upgrade_network(args.infile, args.outfile)
        except exceptions.FastrToolUnknownError as exception:
            fastr.log.error('Encountered exception: {}'.format(exception))
    elif resource_type == 'tool':
        upgrade_tool(input_file, output_file)
    else:
        fastr.log.error(f'Invalid resource type, should be "network" or "tool", found {resource_type}')


if __name__ == '__main__':
    main()
