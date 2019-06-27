#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import print_function

import os
import logging
from datetime import datetime

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--token', default=os.environ.get('GITLAB_TOKEN'))

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    try:
        import gitlab
    except ImportError:
        parser.error('install python-gitlab to be able to use this script')

    if not args.token:
        parser.error('either set GITLAB_TOKEN or pass the --token option')

    server = gitlab.Gitlab('https://gitlab.cern.ch/', args.token)

    logging.debug('retrieve group lhcb-datapkg')
    group = server.groups.get('lhcb-datapkg')
    logging.debug('listing projects in %s', group.name)
    packages = set(p.path for p in group.projects.list(all=True))

    logging.debug('looping over subgroups')
    for subgroup in group.subgroups.list(all=True):
        logging.debug('retrieve subgroup %s', subgroup.name)
        g = server.groups.get(subgroup.id)

        logging.debug('listing projects in %s', g.name)
        packages.update('{}/{}'.format(g.path, p.path)
                        for p in g.projects.list(all=True))

    print('# List of known package names in gitlab')
    print('# generated at %s by %s' % (datetime.now(), parser.prog))
    print('\n'.join(sorted(packages)))


if __name__ == '__main__':
    main()
