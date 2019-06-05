from esgf_scraper.config import ConfigLoader

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


conf = ConfigLoader()
