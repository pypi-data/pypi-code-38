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
import re
import subprocess
import sys
from fastr.utils.cmd import add_parser_doc_link


def directory(path):
    """
    Make sure the path is a valid directory for argparse
    """
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        raise ValueError('Reference should be a valid directory')
    return path


def tool(value):
    """
    Make sure the value is a correct tool for argparse or reference directory
    """
    import fastr
    try:
        return fastr.tools[value]
    except fastr.exceptions.FastrError:
        return directory(value)


def check_tool(args):
    import fastr

    if isinstance(args.tool, str):
        tool_ref_file = os.path.join(args.tool, fastr.core.tool.Tool.TOOL_REFERENCE_FILE_NAME)
        if os.path.isfile(tool_ref_file):
            fastr.core.tool.Tool.test_tool(args.tool)
        else:
            fastr.log.warning('Could not find valid reference data in {}'.format(args.tool))
    else:
        try:
            fastr.log.info('Testing Tool {} {}'.format(args.tool.ns_id, args.tool.command_version))
            args.tool.test()
        except fastr.exceptions.FastrValueError as e:
            fastr.log.error('Tool is not valid: {}'.format(e))


def check_tools(args):
    import fastr

    for (_, _, _), tool in sorted(fastr.tools.items()):
        if tool.tests is not None and len(tool.tests) > 0:
            # Suppress logging during test
            old_level = fastr.config.loglevel
            fastr.config.loglevel = 50
            result = tool.test()
            fastr.config.loglevel = old_level

            if len(result) > 0:
                fastr.log.info('{}/{}: FAILED'.format(tool.ns_id, tool.command_version))
            else:
                fastr.log.info('{}/{}: PASSED'.format(tool.ns_id, tool.command_version))


def check_network(args):
    import fastr

    # Test if it is a Network or Tool reference directory
    network_file = os.path.join(args.reference, fastr.Network.NETWORK_DUMP_FILE_NAME)

    if os.path.isfile(network_file):
        fastr.log.info('Found Network reference data, testing network')
        fastr.Network.test(args.reference)
    else:
        fastr.log.warning('Could not find valid network reference data in {}'.format(args.reference))


def check_networks(args):
    import fastr

    # Try to test all subdirectories (use them as reference dir)
    subdirs = sorted(x for x in os.listdir(args.reference) if os.path.isdir(os.path.join(args.reference, x)))
    results = []

    for subdir in sorted(subdirs):
        network_dir = os.path.join(args.reference, subdir)

        print('Testing {}... '.format(network_dir)),
        sys.stdout.flush()

        # Make sure the directory is a valid test directory
        if not os.path.exists(os.path.join(network_dir, fastr.Network.NETWORK_DUMP_FILE_NAME)):
            print('SKIPPED')
            continue

        # Create a result entry
        result = {
            'name': subdir,
            'reference': network_dir,
        }

        results.append(result)

        # Run the test in a subprocess (to isolate tests and
        # avoid resource hogging between tests)
        command = ['fastr', 'test', 'network', network_dir]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Save results
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['return_code'] = process.returncode

        # Check if result is valid
        passed = len(stderr) == process.returncode == 0
        passed = passed and re.search(r'^\[INFO\] *network:\d\d\d\d >> Run and reference were equal! Test passed!$',
                                      stdout,
                                      re.MULTILINE) is not None

        result['passed'] = passed
        if len(stderr) == 0:
            print('PASSED' if passed else 'FAILED')
        else:
            print('ERROR')

    if args.result:
        from fastr.helpers.iohelpers import save_json
        save_json(args.result, results)

    if all(x['passed'] for x in results):
        print('ALL TEST PASSED')
    else:
        print('ENCOUNTERED FAILURES')

    return results


def get_parser():
    parser = argparse.ArgumentParser(description="Run a tests for a fastr resource.")
    subparsers = parser.add_subparsers(help='There are different resources that can be tested')

    tool_parser = subparsers.add_parser('tool', help='Test a single tool')
    tool_parser.add_argument('tool', metavar='TOOL', type=tool,
                             help='Tool to test or directory with tool reference data')
    tool_parser.set_defaults(func=check_tool)

    tools_parser = subparsers.add_parser('tools', help='Test all tools known to fastr')
    tools_parser.set_defaults(func=check_tools)

    network_parser = subparsers.add_parser('network', help='Test a single network')
    network_parser.add_argument('reference', metavar='NETWORK', type=directory,
                                help='The reference data to test the Network')
    network_parser.set_defaults(func=check_network)

    networks_parser = subparsers.add_parser('networks', help='Test all network references inside subdirectories')
    networks_parser.add_argument('reference', metavar='REFERENCE', type=directory,
                                 help='path of the directory containing subdirectories with reference data')
    networks_parser.add_argument('--result', metavar='RESULT.json', type=str, required=False,
                                 help='Write the results of the test to a JSON file')
    networks_parser.set_defaults(func=check_networks)
    return parser


def main():
    """
    Run the tests of a tool to verify the proper function
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args, unknown_args = parser.parse_known_args()

    # Ship off subparser to correct function
    args.func(args)


if __name__ == '__main__':
    main()
