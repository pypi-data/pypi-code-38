import sys
from setuptools import setup, find_packages

__version__ = '0.6'
__author__ = 'Barcelona Biomedical Genomics Lab'

if sys.hexversion < 0x02070000:
    raise RuntimeError('This package requires Python 2.7 or later.')

setup(
    name="bgreference",
    version=__version__,
    packages=find_packages(),
    author=__author__,
    description="Simple and fast genome reference retrieve",
    license="Apache License 2",
    url="https://bitbucket.org/bgframework/bgreference",
    download_url="https://bitbucket.org/bgframework/bgreference/get/"+__version__+".tar.gz",
    install_requires=['bgconfig >= 0.2', 'bgdata >= 0.25'],
    classifiers=[],
    package_data={'': ['*.template', '*.template.spec']},
    entry_points={
        'console_scripts': [
            'bgreference = bgreference.utils:cmdline'
        ]
    }
)
