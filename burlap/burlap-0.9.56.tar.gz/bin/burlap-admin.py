#!/usr/bin/env python
"""
Command line tool for initializing Burlap-structured Django projects.

e.g.

    burlap skel --name=myproject
"""
from __future__ import print_function

import argparse
import os
import sys

_path = os.path.normpath(os.path.join(os.path.realpath(__file__), '../..'))
sys.path.insert(0, _path)

import burlap # pylint: disable=wrong-import-position
from burlap.project import project # pylint: disable=wrong-import-position

ACTIONS = (
    SKEL,
    ADD_ROLE,
    CREATE_SATCHEL,
) = (
    'skel',
    'add-role',
    'create-satchel',
)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=('Initialize and manage a Burlap structured project.'),
    )
    parser.add_argument(
        '-v', '--version',
        help='Show version.',
        action='version',
        version=burlap.__version__,
    )
    subparsers = parser.add_subparsers(dest='action')

    skel_parser = subparsers.add_parser(
        SKEL,
        help='Creates a skeleton project.')
    skel_parser.add_argument(
        'project_name',
        type=str,
        help='project name')
    skel_parser.add_argument(
        '--pip-requirements',
        type=str,
        default='Fabric',
        help='The default Python packages to install.')
    skel_parser.add_argument(
        '--virtualenv-dir',
        type=str,
        default='.env',
        help='The default virtualenv directory.')
    skel_parser.add_argument(
        '--roles',
        type=str,
        default='',#dev,prod',
        help='The default roles to populate.')
    skel_parser.add_argument(
        '--components',
        type=str,
        default='',
        help='The default components to enable (e.g. django).')
    skel_parser.add_argument(
        '--dj-version',
        type=str,
        default='',
        help='If the component dj is specified, the version of Django to install.')

    add_role_parser = subparsers.add_parser(
        ADD_ROLE,
        help='Adds a new role to the project.')
    add_role_parser.add_argument(
        'roles', metavar='roles', type=str, nargs='+',
        help='Names of roles to add.')

    create_satchel_parser = subparsers.add_parser(
        CREATE_SATCHEL,
        help='Adds a new role to the project.')
    create_satchel_parser.add_argument(
        'name', type=str,
        help='Names of the satchel to create.')

    args = parser.parse_args()
    if args.action == SKEL:
        project.create_skeleton(**args.__dict__)
    elif args.action == ADD_ROLE:
        project.add_roles(args.roles)
    elif args.action == CREATE_SATCHEL:
        project.create_satchel(args.name)
    else:
        raise NotImplementedError('Unknown action: %s' % (args.action))
