from __future__ import print_function

import os
import sys
import re
import json

from fabric.api import (
    settings,
    runs_once,
)

try:
    import boto
except ImportError:
    boto = None

import six

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task

S3SYNC_PATH_PATTERN = r'(?:->)\s+([^\n]+)'

class S3Satchel(Satchel):

    name = 's3'

    def set_defaults(self):
        # {name:[dict(local_path='static/', remote_path='$AWS_BUCKET:/')]}
        self.env.sync_sets = {}
        self.env.media_postfix = ''
        self.env.sync_enabled = False
        self.env.s3cmd_path = '{virtualenv_bin_dir}/s3cmd'

    @task
    @runs_once
    def sync(self, sync_set, force=0, site=None, role=None):
        """
        Uploads media to an Amazon S3 bucket using s3sync.

        Requires s3cmd. Install with:

            pip install s3cmd

        """
        from burlap.dj import dj
        force = int(force)

        r = self.local_renderer

        r.env.sync_force_flag = ' --force ' if force else ''

        _settings = dj.get_settings(site=site, role=role)
        assert _settings, 'Unable to import settings.'
        for k in _settings.__dict__.keys():
            if k.startswith('AWS_'):
                r.genv[k] = _settings.__dict__[k]

        site_data = r.genv.sites[r.genv.SITE]
        r.env.update(site_data)

        r.env.virtualenv_bin_dir = os.path.split(sys.executable)[0]

        rets = []
        for paths in r.env.sync_sets[sync_set]:
            is_local = paths.get('is_local', True)
            local_path = paths['local_path'] % r.genv
            remote_path = paths['remote_path']
            remote_path = remote_path.replace(':/', '/')
            if not remote_path.startswith('s3://'):
                remote_path = 's3://' + remote_path
            local_path = local_path % r.genv

            if is_local:
                #local_or_dryrun('which s3sync')#, capture=True)
                r.env.local_path = os.path.abspath(local_path)
            else:
                #run('which s3sync')
                r.env.local_path = local_path

            if local_path.endswith('/') and not r.env.local_path.endswith('/'):
                r.env.local_path = r.env.local_path + '/'

            r.env.remote_path = remote_path % r.genv

            print('Syncing %s to %s...' % (r.env.local_path, r.env.remote_path))

            # Superior Python version.
            if force:
                r.env.sync_cmd = 'put'
            else:
                r.env.sync_cmd = 'sync'
            r.local(
                'export AWS_ACCESS_KEY_ID={aws_access_key_id}; '\
                'export AWS_SECRET_ACCESS_KEY={aws_secret_access_key}; '\
                '{s3cmd_path} {sync_cmd} --progress --acl-public --guess-mime-type --no-mime-magic '\
                '--delete-removed --cf-invalidate --recursive {sync_force_flag} '\
                '{local_path} {remote_path}')

    @task
    def invalidate(self, *paths):
        """
        Issues invalidation requests to a Cloudfront distribution
        for the current static media bucket, triggering it to reload the specified
        paths from the origin.

        Note, only 1000 paths can be issued in a request at any one time.
        """
        dj = self.get_satchel('dj')
        if not paths:
            return
        # http://boto.readthedocs.org/en/latest/cloudfront_tut.html
        _settings = dj.get_settings()
        if not _settings.AWS_STATIC_BUCKET_NAME:
            print('No static media bucket set.')
            return
        if isinstance(paths, six.string_types):
            paths = paths.split(',')
        all_paths = list(map(str.strip, paths))
        i = 0
        while 1:
            paths = all_paths[i:i+1000]
            if not paths:
                break

            c = boto.connect_cloudfront()
            rs = c.get_all_distributions()
            target_dist = None
            for dist in rs:
                print(dist.domain_name, dir(dist), dist.__dict__)
                bucket_name = dist.origin.dns_name.replace('.s3.amazonaws.com', '')
                if bucket_name == _settings.AWS_STATIC_BUCKET_NAME:
                    target_dist = dist
                    break
            if not target_dist:
                raise Exception(('Target distribution %s could not be found in the AWS account.') % (settings.AWS_STATIC_BUCKET_NAME,))
            print('Using distribution %s associated with origin %s.' % (target_dist.id, _settings.AWS_STATIC_BUCKET_NAME))
            inval_req = c.create_invalidation_request(target_dist.id, paths)
            print('Issue invalidation request %s.' % (inval_req,))
            i += 1000

    @task
    def get_or_create_bucket(self, name):
        """
        Gets an S3 bucket of the given name, creating one if it doesn't already exist.

        Should be called with a role, if AWS credentials are stored in role settings. e.g.

            fab local s3.get_or_create_bucket:mybucket
        """
        from boto.s3 import connection
        if self.dryrun:
            print('boto.connect_s3().create_bucket(%s)' % repr(name))
        else:
            conn = connection.S3Connection(
                self.genv.aws_access_key_id,
                self.genv.aws_secret_access_key
            )
            bucket = conn.create_bucket(name)
            return bucket

    @task
    def list_bucket_sizes(self):

        UNIT_TO_BYTES = {
            'Bytes': 1,
            'KiB': 1000,
            'MiB': 1000000,
            'GiB': 1000000000,
        }

        r = self.local_renderer

        sizes = {} # {bucket: total size}
        total_size_bytes = 0

        buckets = json.loads(r.local("aws s3api list-buckets --query 'Buckets[].Name'", capture=True) or '[]')
        print('buckets:', len(buckets))

        for bucket in buckets:
            ret = r.local("aws s3 ls --summarize --human-readable --recursive s3://%s/" % bucket, capture=True)
            matches = re.findall(r'Total Size: (?P<number>[0-9\.]+)\s(?P<unit>[a-zA-Z]+)', ret)
            print('matches:', matches)
            value, unit = matches[0]
            value = float(value) * UNIT_TO_BYTES[unit]
            total_size_bytes += value
            sizes[bucket] = value
        print()
        print('name,bytes')
        for name in sorted(sizes):
            print('%s,%s' % (name, sizes[name]))
        print('all,%s' % total_size_bytes)

    @task(precursors=['packager'])
    def configure(self, *args, **kwargs):
        pass

s3 = S3Satchel()
