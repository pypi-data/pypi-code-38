import sys

import pkg_resources

from supervisor.compat import as_string


def main(out=sys.stdout):
    config = pkg_resources.resource_string(__name__, 'skel/sample.conf')
    out.write(as_string(config))
