from setuptools import find_packages, setup
import sys

PYTHON_VERSION = (3, 6)

if sys.version_info < PYTHON_VERSION:
    sys.exit("openformat requires python %s or newer. You have python %s." %
             (PYTHON_VERSION, sys.version_info))

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='openformat',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.3',
        'scipy>=0.7',
    ],
    version="0.2.2",
    author="Till Hoffmann",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
