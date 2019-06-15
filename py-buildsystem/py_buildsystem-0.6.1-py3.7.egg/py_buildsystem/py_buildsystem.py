import sys
import argparse

from py_buildsystem.common import logger, levels

from py_buildsystem.Project.Project import Project
from py_buildsystem.Toolchain.Toolchain import Toolchain


sys.tracebacklimit = 0


parser = argparse.ArgumentParser(usage="python -m py_buildsystem [options]", description='Python based build system.')

parser.add_argument('compiler_config', metavar='CC', type=str, nargs=1,
                    help='Compiler configuration file')

parser.add_argument('project_config', metavar='PC', type=str, nargs=1,
                    help='Project configuration file')

parser.add_argument('compiler_path', metavar='path', type=str, nargs='?', default='',
                    help='Path to compiler')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='verbose mode')

args = parser.parse_args()

if args.v is True:
    logger.setLevel(levels["DEBUG"])
else:
    logger.setLevel(levels["INFO"])

toolchain = Toolchain(args.compiler_config[0], args.compiler_path)
project = Project(args.project_config[0], toolchain)
