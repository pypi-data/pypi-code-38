# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import argparse
import pkg_resources
from .maya_utils import run_batch
from colorama import init
init(autoreset=True)

__version__ = "0.2.0"

if os.environ.get('COVERAGE_PROCESS_START'):
    import coverage
    coverage.process_startup()

def maya_info(*args):
    if args[0].version:
        print(__version__)
    else:
        print('please run "maya {positional argument} --help" to see maya guidance')

def parse_args():
    '''Definite the arguments users need to follow and input'''
    parser = argparse.ArgumentParser(prog='maya', description='use maya command to control nni experiments')
    parser.add_argument('--version', '-v', action='store_true')
    parser.set_defaults(func=maya_info)

    # create subparsers for args with sub values
    subparsers = parser.add_subparsers()

    # parse start command
    parser_start = subparsers.add_parser('B', help='run command with multiprocess.')
    parser_start.add_argument('--command', '-c', required=True, dest='command', help='command to run')
    parser_start.add_argument('--source_dir', '-s', required=True,dest='source_dir',help='source dir')
    parser_start.add_argument('--target_dir', '-t',dest='target_dir', help='target dir')
    parser_start.add_argument('--debug', '-d', action='store_true', help='set debug mode')
    parser_start.set_defaults(func=run_batch)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    parse_args()