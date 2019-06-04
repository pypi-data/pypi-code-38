from __future__ import print_function
from __future__ import division

import os
import yaml

FILEIDCACHE_FILE = '~/.civiscompute/fileidcache.db'
LASTSCRIPTID_LOC = '~/.civiscompute/lastscriptid'


def get_defaults():
    defaults = {
        'use_file_cache': False,
        'required_resources': {
            'cpu': 1024, 'memory': 8192, 'disk_space': 16.0},
        'docker_image_name': {
            'python': 'civisanalytics/datascience-python',
            'r': 'civisanalytics/datascience-r'},
        'repo_cmd': {
            'python': 'python setup.py install',
            'r': None},
        'add_aws_creds': False,
        'aws_cred_id': None}

    config_loc = os.path.expanduser('~/.civiscompute/config.yml')
    if os.path.exists(config_loc):
        with open(config_loc, 'r') as fp:
            defaults.update(yaml.safe_load(fp))

    return defaults
