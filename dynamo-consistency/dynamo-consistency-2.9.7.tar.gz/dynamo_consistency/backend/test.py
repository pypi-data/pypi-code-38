# pylint: disable=missing-docstring, unused-argument, invalid-name

"""
This module defines dummy variables as needed by
dynamo_consistency.backend for running tests with
"""


import os
import logging
import datetime

from .. import config


LOG = logging.getLogger(__name__)


_FILES = sorted([
    ('/store/mc/ttThings/0000/qwert.root', 20),
    ('/store/mc/ttThings/0000/qwery.root', 30),
    ('/store/data/runB/0001/orphan.root', 45),
    ('/store/data/runA/0030/stuff.root', 10),
    ('/store/data/runC/0000/emtpy/dir', ),
    ('/store/logs/prod/recent/test.tar.gz', 20),
    ('/store/logs/prod/nope/test.tar.gz', 20),
    ])

_INV = sorted([
    ('/store/mc/ttThings/0000/qwert.root', 20),
    ('/store/mc/ttThings/0000/qwery.root', 30),
    ('/store/data/runB/0003/missing.root', 45),
    ('/store/data/runA/0030/stuff.root', 10),
    ])

# These are all the methods needed from inventory
class _Inventory(object):
    @staticmethod
    def protected_datasets(site):
        return set()
    @staticmethod
    def list_files(site):
        return [(name, size, datetime.datetime.fromtimestamp(1)) for
                name, size in _INV]


class _Registry(object):
    def __init__(self):
        self.deleted = []
        self.transfered = []

    def _reset(self):
        self.deleted = []
        self.transfered = []

    def delete(self, site, files):
        self.deleted.extend(files)
        self.deleted.sort()
        return len(files)

    def transfer(self, site, files):
        # This overwrites previous transfer call
        self.transfered = [(site, fil) for fil in files]
        return [], []


class _SiteInfo(object):
    @staticmethod
    def site_list():
        return ['TEST_SITE', 'BAD_SITE']
    @staticmethod
    def ready_sites():
        return set(['TEST_SITE'])


TMP_DIR = 'TempConsistency'


def _ls(path, location=TMP_DIR):

    LOG.debug('_ls(%s, %s)', path, location)

    full_path = os.path.join(location, path[len(config.config_dict()['RootPath']) + 1:])

    if os.path.exists(full_path):
        results = [os.path.join(full_path, res) for res in os.listdir(full_path)]

        dirs = [(os.path.basename(name), os.stat(name).st_mtime)
                for name in results if os.path.isdir(name)]
        files = [(os.path.basename(name), os.stat(name).st_size, os.stat(name).st_mtime)
                 for name in results if os.path.isfile(name)]

        return True, dirs, files

    dirs = []
    files = []
    for fil in _FILES:
        LOG.debug('Considering %s against %s', fil, path)
        if fil[0].startswith(path):
            LOG.debug('Match! %s and %s', fil[0], path)
            element = fil[0][len(path) + (not path.endswith('/')):].split('/')[0]
            if element.endswith('.root') or element.endswith('.tar.gz'):
                files.append((element, fil[1], 1))
            else:
                dirs.append((element, 1))

    LOG.debug('%s, %s, %s', True, dirs, files)

    return True, dirs, files


# The following are all the things imported by dynamo_consistency.backend

inventory = _Inventory()
registry = _Registry()
siteinfo = _SiteInfo()

def filelist_to_blocklist(site, infile, outfile):
    pass

def get_listers(site):
    return _ls, None

def check_site(site):
    return site in siteinfo.ready_sites()

def deletion_requests(site):
    return set()

class DatasetFilter(object):
    def __init__(self, _):
        pass
    @staticmethod
    def protected(_):
        return False
