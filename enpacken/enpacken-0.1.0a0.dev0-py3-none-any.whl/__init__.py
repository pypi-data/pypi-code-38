"""Find package installation candidates."""

import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("enpacken").version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None
