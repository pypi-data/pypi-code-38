from . import entity, indicator
from .merge import DDFPackageCollection

__version__ = "0.5.0"


def merge_packages(paths, dest, include=[]):
    collection = DDFPackageCollection(paths)
    collection.to_package(dest, include)
