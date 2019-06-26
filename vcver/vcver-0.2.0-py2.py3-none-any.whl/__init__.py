import logging
from .version import get_version

LOG = logging.getLogger(__name__)


def setup_keywords_entry_point(dist, attr, value):
    logging.basicConfig()
    version = get_version(**value)
    dist.metadata.version = version
