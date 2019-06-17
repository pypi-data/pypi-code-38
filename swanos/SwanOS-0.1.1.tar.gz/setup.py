from setuptools import *
import setuptools
__project__ = "SwanOS"
__version__ = "0.1.1"
__description__ = "A Very Simple Python OS"
__classifiers__ = [
    "Programming Language :: Python :: 3",
]
__author_email__ = 'forsbergw82@gmail.com'
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = setuptools.find_packages(),
    classifiers = __classifiers__,
    author_email = __author_email__,
    long_description=long_description,
    long_description_content_type="text/markdown",
)