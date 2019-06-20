from setuptools import setup
import sys

if sys.version_info < (3, 4):
    raise RuntimeError(
        'Python versions previous to 3.4 are not supported'
    )

setup(
    name='setuptools-setup-versions',

    version="0.0.21",

    description=(
        "Automatically update setup.py `install_requires` version numbers"
        "for PIP packages"
    ),

    author='David Belais',
    author_email='david@belais.me',

    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    keywords='setuptools install_requires version',

    packages=['setuptools_setup_versions'],

    install_requires=[
        "setuptools>=39.0.1",
        "pip>=19.1.1",
        "more-itertools>=7.0.0"
    ]
)