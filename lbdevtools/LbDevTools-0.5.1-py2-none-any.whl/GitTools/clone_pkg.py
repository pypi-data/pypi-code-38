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

import git
import logging
from subprocess import CalledProcessError
from LbDevTools.GitTools.common import (
    add_protocol_argument, handle_protocol_argument, add_verbosity_argument,
    handle_verbosity_argument, add_version_argument, package_url)


def get_latest_tag(repo):
    try:
        return repo.git.describe(match='v*', abbrev=0, tags=True)
    except git.GitCommandError:
        from LbEnv.ProjectEnv.version import isValidVersion, versionKey
        logging.debug('no tag in current branch of %s', repo.working_dir)
        all_tags = [t.name for t in repo.tags if isValidVersion('', t.name)]
        if all_tags:
            all_tags.sort(key=versionKey)
            return all_tags[-1]
        return None


XENV_DELEGATION = '''<?xml version="1.0" encoding="UTF-8"?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema EnvSchema.xsd ">
  <env:include>../{name}</env:include>
</env:config>'''


def main():
    import os
    from os.path import join, exists, basename
    from argparse import ArgumentParser
    parser = ArgumentParser(description='wrapper around "git clone" to get '
                            'data packages')
    add_version_argument(parser)

    parser.add_argument('url', nargs='?', help='git URL to use')
    parser.add_argument('name', help='name of the data package')

    git_group = parser.add_argument_group("'git clone' arguments")
    git_group.add_argument(
        '-o',
        '--origin',
        metavar='NAME',
        help="use NAME instead of 'origin' to track "
        "upstream")
    git_group.add_argument(
        '-b',
        '--branch',
        help='checkout BRANCH instead of the remote\'s '
        'HEAD')

    add_protocol_argument(parser)
    add_verbosity_argument(parser)

    parser.set_defaults(branch='master')

    args = parser.parse_args()
    handle_verbosity_argument(args)

    handle_protocol_argument(args)

    if not args.url:
        args.url = package_url(args.name, args.protocol)

    try:
        logging.info('cloning %s@%s to %s', args.url, args.branch, args.name)
        repo = git.Repo.clone_from(args.url, args.name, branch=args.branch)

        logging.debug('initializing data package')
        xml_env = args.name.replace('/', '_') + '.xenv'
        old_xml_env = join(args.name,
                           args.name.replace('/', '_') + 'Environment.xml')
        if not exists(old_xml_env):
            logging.debug(' - adding %s', basename(old_xml_env))
            os.symlink(xml_env, old_xml_env)

        # guess version aliases
        version_aliases = ['v999r999']
        if exists(join(args.name, 'cmt', 'requirements')):
            for l in open(join(args.name, 'cmt', 'requirements')):
                l = l.strip()
                if l.startswith('version'):
                    version = l.split()[1]
                    version_aliases.append(version[:version.rfind('r')] +
                                           'r999')
                    break
        else:
            version = get_latest_tag(repo)
            if version:
                version_aliases.append(version[:version.rfind('r')] + 'r999')
        logging.debug(' - creating fake entries in %s in %s', version_aliases,
                      args.name)
        for version in version_aliases:
            os.makedirs(join(args.name, version))
            for name in (xml_env, basename(old_xml_env)):
                with open(join(args.name, version, name), 'w') as f:
                    f.write(XENV_DELEGATION.format(name=name))

    except CalledProcessError as exc:
        exit(exc.returncode)
