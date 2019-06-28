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
from argparse import ArgumentParser
from LbEnv import fixProjectCase
from LbDevTools.GitTools.common import (
    add_protocol_argument, handle_protocol_argument, add_verbosity_argument,
    handle_verbosity_argument, add_version_argument, project_url)


def main():
    '''
    Implementation of `git lb-use` command.
    '''

    parser = ArgumentParser(prog='git lb-use')
    add_version_argument(parser)

    parser.add_argument('project', help='project which history to fetch')
    parser.add_argument(
        'url',
        nargs='?',
        metavar='repository_url',
        help='alternative repository to use, instead of the '
        'standard one')

    add_protocol_argument(parser)
    add_verbosity_argument(parser)

    args = parser.parse_args()
    handle_verbosity_argument(args)

    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        logging.error('current directory is not a Git repository')
        exit(1)

    handle_protocol_argument(args, repo)

    project = fixProjectCase(args.project)
    if args.project != project:
        logging.warnins('misspelled project name, using %s instead', project)
        args.project = project
    del project

    if not args.url:
        args.url = project_url(args.project, args.protocol)

    logging.info("calling: git remote add -f '%s' '%s'", args.project,
                 args.url)

    # define a remote "$project", overwrite it if it already exists
    try:
        old_url = repo.remote(args.project).url
        # the remote is defined
        logging.warning("overwriting existing remote '%s' (was %s)",
                        args.project, old_url)
        repo.delete_remote(args.project)
    except ValueError:  # remote does not exist
        pass

    try:
        remote = repo.create_remote(args.project, args.url)
        with remote.config_writer as conf:
            conf.set('tagopt', '--no-tags')
        # FIXME 'git config --add' is not supported bug GitPython
        repo.git.config(
            'remote.{}.fetch'.format(args.project),
            '+refs/tags/*:refs/tags/{}/*'.format(args.project),
            add=True)
        refs = remote.fetch()

        TAGS = True
        BRANCHES = False
        groups = {TAGS: [], BRANCHES: []}
        for ref in refs:
            groups[hasattr(ref.ref, 'tag')].append(ref)
        logging.info('fetched %d branches and %d tags', len(groups[BRANCHES]),
                     len(groups[TAGS]))
        if groups[BRANCHES]:
            logging.debug('Branches:')
            [logging.debug(' - %s', ref.name) for ref in groups[BRANCHES]]
        if groups[TAGS]:
            logging.debug('Tags:')
            [logging.debug(' - %s', ref.name) for ref in groups[TAGS]]
    except Exception as err:
        logging.error('%s: %s', type(err).__name__, err)
        exit(1)
