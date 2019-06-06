import codecs
import re
import os.path
from setuptools import setup, find_packages

def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fp):
    return codecs.open(fpath(fp), encoding="utf-8").read()


install_requires = [
    "Cartopy>=0.17.0",
    "descartes>=1.1.0",
    "geopandas>=0.4.1",
    "netCDF4==1.5.0.1",
    "numpy>=1.16.2",
    "matplotlib>=3.0.3",
    "pandas>=0.24.2",
    "pyproj>=2.1.2",
    "pyepsg>=0.4.0",
    "rasterio>=1.0.22",
    "requests>=2.21.0",
    "sentinelsat>=0.13",
    "scipy>=1.2.1",
    "Shapely>=1.6.4",
]

with open("README.md", "r") as f:
    long_description = f.read()

version = {}
with open(os.path.join("src", "geotoys", "version.py"), "r") as f:
    exec(f.read(), version)

setup(
    name="geotoys",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version=version["__version__"],
    url="https://github.com/ryanjdillon/geotoys",
    license="MIT",
    maintainer="Ryan J. Dillon",
    description="Tools for working with geospatial data in python",
    long_description=long_description,
    long_description_type="text/markdown",
    install_requires=install_requires,
    test_suite="tests",
)
