###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

import os
import logging
import stat
import sys

from string import Template

import LbEnv.ProjectEnv
from LbEnv.ProjectEnv.version import DEFAULT_VERSION, expandVersionAlias
from LbEnv import fixProjectCase
from LbDevTools import createGitIgnore, createClangFormat, DATA_DIR


def main():
    '''
    Script to generate a local development project.
    '''
    from argparse import ArgumentParser, SUPPRESS
    from LbEnv.ProjectEnv.options import (
        addSearchPath, addOutputLevel, addPlatform, addListing, checkPlatform)
    from LbEnv.ProjectEnv.lookup import findProject, MissingProjectError
    from LbDevTools.GitTools.common import add_version_argument
    from subprocess import call

    parser = ArgumentParser()

    parser.add_argument('project',
                        metavar='Project[/version]',
                        help='Name and optional version of the project to use')
    parser.add_argument('version',
                        nargs='?',
                        help=SUPPRESS)

    addSearchPath(parser)
    addOutputLevel(parser)
    addPlatform(parser)
    addListing(parser)

    def project_name(name):
        'make sure name is a valid identifier'
        import re
        if not re.match(r'^[a-z_][0-9a-z_]*$', name, re.IGNORECASE):
            raise ValueError('invalid name')
        return name

    project_name.__name__ = 'project name'  # nicer printout for errors

    parser.add_argument(
        '--name',
        type=project_name,
        help='Name of the local project [default: "<proj>Dev_<vers>"].')

    parser.add_argument(
        '--dest-dir',
        help='Where to create the local project [default: %(default)s].',
        default=os.curdir)

    parser.add_argument(
        '--git',
        action='store_true',
        help='Initialize git repository in the generated directory [default, '
        'if git is available].')

    parser.add_argument(
        '--no-git',
        action='store_false',
        dest='git',
        help='Do not initialize the git local repository.')

    parser.add_argument(
        '--with-fortran',
        action='store_true',
        help='enable FORTRAN support for the generated project')

    parser.add_argument(
        '--without-fortran',
        action='store_false',
        dest='with_fortran',
        help='do not enable FORTRAN support for the generated project (default)'
    )

    add_version_argument(parser)

    from whichcraft import which
    parser.set_defaults(git=bool(which('git')), with_fortran=False)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    args.platform = checkPlatform(parser, args.platform)

    if args.version:
        logging.warning(
            'deprecated version specification: '
            'use "lb-dev ... %s/%s" instead', args.project, args.version)
        args.project = '/'.join((args.project, args.version))

    if '/' in args.project:
        args.project = tuple(args.project.split('/', 1))
    else:
        args.project = (args.project, DEFAULT_VERSION)

    try:
        project, version = args.project
        version = expandVersionAlias(project, version, args.platform)
    except ValueError:
        parser.error('wrong number of arguments')

    project = fixProjectCase(project)

    try:
        from LbEnv.ProjectEnv.lookup import InvalidNightlySlotError
        from LbEnv.ProjectEnv.script import localNightlyHelp
        if isinstance(args.nightly, InvalidNightlySlotError):
            sys.stderr.write(
                localNightlyHelp(
                    parser.prog or os.path.basename(sys.argv[0]), args.nightly,
                    project, args.platform
                    if args.platform not in ('best', None) else '$CMTCONFIG',
                    sys.argv[1:]))
            sys.exit(64)
        if args.help_nightly_local:
            if not args.nightly:
                parser.error('--help-nightly-local must be specified in '
                             'conjunction with --nightly')
            sys.stdout.write(
                localNightlyHelp(
                    parser.prog or os.path.basename(sys.argv[0]),
                    InvalidNightlySlotError(args.nightly[0], args.nightly[1],
                                            []),
                    project,
                    args.platform
                    if args.platform not in ('best', None) else '$CMTCONFIG', [
                        a for a in sys.argv[1:]
                        if not '--help-nightly-local'.startswith(a)
                    ],
                    error=False))
            sys.exit()
    except ImportError:
        # old version of LbEnv
        # (before https://gitlab.cern.ch/lhcb-core/LbEnv/merge_requests/19)
        pass

    if args.user_area and not args.no_user_area:
        from LbEnv.ProjectEnv import EnvSearchPathEntry, SearchPathEntry
        if os.environ['User_release_area'] == args.user_area:
            args.dev_dirs.insert(0, EnvSearchPathEntry('User_release_area'))
        else:
            args.dev_dirs.insert(0, SearchPathEntry(args.user_area))

    # FIXME: we need to handle common options like --list in a single place
    if args.list:
        from LbEnv.ProjectEnv.lookup import listVersions
        for entry in listVersions(project, args.platform):
            print '%s in %s' % entry
        sys.exit(0)
    if args.list_platforms:
        from LbEnv.ProjectEnv.lookup import listPlatforms
        platforms = listPlatforms(project, version)
        if platforms:
            print '\n'.join(platforms)
        sys.exit(0)

    if not args.name:
        args.name = '{project}Dev_{version}'.format(
            project=project, version=version)
        local_project, local_version = project + 'Dev', version
    else:
        local_project, local_version = args.name, 'HEAD'

    devProjectDir = os.path.join(args.dest_dir, args.name)

    if os.path.exists(devProjectDir):
        parser.error('directory "%s" already exist' % devProjectDir)

    # ensure that the project we want to use can be found

    # prepend dev dirs to the search path
    if args.dev_dirs:
        LbEnv.ProjectEnv.path[:] = args.dev_dirs + LbEnv.ProjectEnv.path

    try:
        try:
            projectDir = findProject(project, version, args.platform)
            logging.info('using %s %s from %s', project, version, projectDir)
        except MissingProjectError, x:
            parser.error(str(x))

        # Check if it is a CMake-enabled project
        use_cmake = os.path.exists(
            os.path.join(projectDir, project + 'Config.cmake'))
        if not use_cmake:
            logging.warning('%s %s does not seem a CMake project', project,
                            version)

        # Check if it is a CMT-enabled project
        use_cmt = os.path.exists(
            os.path.join(projectDir, os.pardir, os.pardir, 'cmt',
                         'project.cmt'))

        if not use_cmake and not use_cmt:
            logging.error('neither CMake nor CMT configuration found '
                          '(are you using the right CMTCONFIG?)')
            exit(1)
    except SystemExit as err:
        if args.nightly:
            try:
                from LbEnv.ProjectEnv.lookup import InvalidNightlySlotError
                from LbEnv.ProjectEnv.script import localNightlyHelp
                sys.stderr.write(
                    localNightlyHelp(
                        parser.prog or os.path.basename(sys.argv[0]),
                        InvalidNightlySlotError(args.nightly[0],
                                                args.nightly[1], []), project,
                        args.platform if args.platform not in ('best', None)
                        else '$CMTCONFIG', sys.argv[1:]))
            except ImportError:
                # old version of LbEnv
                # (before https://gitlab.cern.ch/lhcb-core/LbEnv/merge_requests/19)
                pass
        sys.exit(err.code)

    # Create the dev project
    if not os.path.exists(args.dest_dir):
        logging.debug('creating destination directory "%s"', args.dest_dir)
        os.makedirs(args.dest_dir)

    logging.debug('creating directory "%s"', devProjectDir)
    if args.git:
        call(['git', 'init', '--quiet', devProjectDir])
    else:
        os.makedirs(devProjectDir)

    data = dict(
        project=project,
        version=version,
        search_path=' '.join(['"%s"' % p for p in LbEnv.ProjectEnv.path]),
        search_path_repr=repr(LbEnv.ProjectEnv.path),
        search_path_env=os.pathsep.join(LbEnv.ProjectEnv.path),
        # we use cmake if available
        build_tool=('cmake' if use_cmake else 'cmt'),
        PROJECT=project.upper(),
        local_project=local_project,
        local_version=local_version,
        with_fortran=' FORTRAN' if args.with_fortran else '',
        cmt_project=args.name,
        datadir=DATA_DIR)

    # FIXME: improve generation of searchPath files, so that they match the command line
    templateDir = os.path.join(
        os.path.dirname(__file__), 'templates', 'lb-dev')
    templates = [
        'CMakeLists.txt', 'toolchain.cmake', 'Makefile', 'searchPath.py',
        'build.conf', 'run'
    ]
    # generated files that need exec permissions
    execTemplates = set(['run'])

    if args.nightly:
        data['slot'], data['day'], data['base'] = args.nightly
    else:
        data['slot'] = data['day'] = data['base'] = ''

    # for backward compatibility, we create the CMT configuration and env helpers
    if use_cmt:
        templates += ['cmt/project.cmt']
        os.makedirs(os.path.join(devProjectDir, 'cmt'))

    for templateName in templates:
        t = Template(open(os.path.join(templateDir, templateName)).read())
        logging.debug('creating "%s"', templateName)
        dest = os.path.join(devProjectDir, templateName)
        with open(dest, 'w') as f:
            f.write(t.substitute(data))
        if templateName in execTemplates:
            mode = (stat.S_IMODE(os.stat(dest).st_mode) | stat.S_IXUSR
                    | stat.S_IXGRP)
            os.chmod(dest, mode)

    # generate searchPath.cmake
    if args.dev_dirs and use_cmake:
        logging.debug('creating "%s"', 'searchPath.cmake')
        dest = os.path.join(devProjectDir, 'searchPath.cmake')
        with open(dest, 'w') as f:
            f.write('# Search path defined from lb-dev command line\n')
            f.write(args.dev_dirs.toCMake())

    if args.dev_dirs and use_cmt:
        for shell in ('sh', 'csh'):
            build_env_name = 'build_env.' + shell
            logging.debug('creating "%s"', build_env_name)
            dest = os.path.join(devProjectDir, build_env_name)
            with open(dest, 'w') as f:
                f.write('# Search path defined from lb-dev command line\n')
                f.write(args.dev_dirs.toCMT(shell))

    # When the project name is not the same as the local project name, we need a
    # fake *Sys package for SetupProject (CMT only).
    if use_cmt and project != local_project:
        t = Template(
            open(os.path.join(templateDir, 'cmt/requirements_')).read())
        templateName = os.path.join(local_project + 'Sys', 'cmt/requirements')
        os.makedirs(os.path.dirname(os.path.join(devProjectDir, templateName)))
        logging.debug('creating "%s"', templateName)
        open(os.path.join(devProjectDir, templateName), 'w').write(
            t.substitute(data))
        if use_cmake:  # add a CMakeLists.txt to it
            with open(
                    os.path.join(devProjectDir, local_project + 'Sys',
                                 'CMakeLists.txt'), 'w') as cml:
                cml.write('gaudi_subdir({0} {1})\n'.format(
                    local_project + 'Sys', local_version))

    # add a default .clang-format file
    upstream_style_file = os.path.join(projectDir, os.pardir, os.pardir,
                                       '.clang-format')
    dev_style_file = os.path.join(devProjectDir, '.clang-format')
    if os.path.exists(upstream_style_file):
        with open(dev_style_file, 'w') as f:
            f.write('# Copied from {}\n'.format(upstream_style_file))
            f.writelines(open(upstream_style_file))
    else:
        # use default
        createClangFormat(dev_style_file)

    if args.git:
        createGitIgnore(
            os.path.join(devProjectDir, '.gitignore'), selfignore=False)
        call(['git', 'add', '.'], cwd=devProjectDir)
        call(
            [
                'git', 'commit', '--quiet', '-m',
                'initial version of satellite project\n\n'
                'generated with:\n\n'
                '    %s\n' % ' '.join(sys.argv)
            ],
            cwd=devProjectDir)

    # Success report
    msg = '''
Successfully created the local project {0} in {1}

To start working:

  > cd {2}
  > git lb-use {3}
  > git lb-checkout {3}/vXrY MyPackage

then

  > make
  > make test

and optionally (CMake only)

  > make install

You can customize the configuration by editing the files 'build.conf' and
'CMakeLists.txt' (see http://cern.ch/gaudi/CMake for details).
'''

    print msg.format(args.name, args.dest_dir, devProjectDir, project)
