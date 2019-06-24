# -*- coding: utf-8 -*-

# Define self package variable
__version__ = '1.1.3.2'
__all__ = ["pycltools"]
__author__= 'Adrien Leger'
__email__ = 'aleg@ebi.ac.uk'
__url__ = "https://github.com/a-slide/pycoQC"
__licence__ = 'GPLv3'
__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3']

__install_requires__ = ['pysam>=0.14.0', 'pandas>=0.23.0', "numpy>=1.14.0", "notebook>=5.6.0", "tqdm>=4.23.4", "httplib2", "paramiko", "matplotlib>=3.0.0"]
__python_requires__='>=3'
__description__= "pycltools is a package written in python3 containing a collection of generic functions and classes for file parsing, manipulation..."

# Collect info in a dictionnary for setup.py
setup_dict = {
    "name":__name__,
    "version":__version__,
    "description": __description__,
    "url":__url__,
    "author": __author__,
    "author_email":__email__,
    "license":__licence__,
    "classifiers": __classifiers__,
    "install_requires": __install_requires__,
    "packages":[__name__],
    "python_requires": __python_requires__,
    }
