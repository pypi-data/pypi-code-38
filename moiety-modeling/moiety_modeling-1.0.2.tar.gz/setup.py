#!/usr/bin/python3

import re
from setuptools import setup, find_packages


def find_version():
    with open('moiety_modeling/__init__.py', 'r') as fd:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            fd.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

REQUIRES = [
    "docopt",
    "jsonpickle",
    "matplotlib",
    "numpy",
    "SAGA-optimize",
    "scipy"
]

setup(

    name='moiety_modeling',
    version=find_version(),
    packages=find_packages(),
    license="The Clear BSD License",
    author="Huan Jin",
    author_email="hji236@g.uky.edu",
    description="Moiety Modeling Implementation",
    keywords="moiety modeling model optimization model selection",
    url="https://github.com/MoseleyBioinformaticsLab/moiety_modeling.git",
    install_requires=REQUIRES,
    long_description=open('README.rst').read(),
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ],


)