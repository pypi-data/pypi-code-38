#!/usr/bin/python3

from io import open
import os

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md'), encoding='utf8').read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''


setup(
    name="pdbme",
    version="0.0.1",
    description="remote pdb which connects to developer",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type='text/markdown',
    author="Łukasz Mach",
    author_email="maho@pagema.net",
    url="http://github.com/mahomahomaho/pdbme",
    packages=["pdbme", "pdbme.arpdb"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Debuggers",
    ],
    requires=['click'],
    scripts=['scripts/pdbme-cli']
)
