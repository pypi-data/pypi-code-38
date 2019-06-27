from __future__ import print_function

import time

import six

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task

def get_boto():
    try:
        import boto
    except ImportError:
        boto = None
    return boto

class CloudfrontSatchel(Satchel):

    name = 'cloudfront'

    def set_defaults(self):
        pass

    @task
    def get_or_create_distribution(self, s3_bucket_name):
        assert isinstance(s3_bucket_name, six.string_types)
        boto = get_boto()
        origin_dns = '%s.s3.amazonaws.com' % s3_bucket_name
        if not self.dryrun:
            conn = boto.connect_cloudfront(
                self.genv.aws_access_key_id,
                self.genv.aws_secret_access_key
            )
            origin = boto.cloudfront.origin.S3Origin(origin_dns)

            distro = None
            if self.verbose:
                # Loop over all distributions to determine whether this one exists already.
                dists = conn.get_all_distributions()
                for d in dists:
                    print('Checking existing Cloudfront distribution %s...' % d.get_distribution().config.origin.dns_name)
                    if origin_dns == d.get_distribution().config.origin.dns_name:
                        print('Found existing distribution!')
                        distro = d
                        break

                    # Necessary to avoid "Rate exceeded" errors.
                    time.sleep(0.4)

            if not distro:
                print('Creating new distribution from %s...' % origin)
                distro = conn.create_distribution(origin=origin, enabled=True)

            return distro
        print('boto.connect_cloudfront().create_distribution(%s)' % repr(origin_dns))

    @task
    def configure(self):
        pass

cloudfront = CloudfrontSatchel()
