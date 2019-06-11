#!/usr/bin/env python
""" Gavia is a Python package built for processing science data from the Gavia Autonomous Underwater Vehicle.
"""

from distutils.core import setup
from setuptools import find_packages

DOCLINES = (__doc__ or '').split("\n")
exec(open('gavia/version.py').read())
setup(name='gavia',
      version=__version__,
      description=DOCLINES[0],
      long_description="\n".join(DOCLINES[0:]),
      url='http://github.com/brett-hosking/gavia',
      license='MIT',
      author='brett hosking',
      author_email='wilski@noc.ac.uk',
      install_requires=[
            "numpy>=1.16.2",
            "imageio>=2.5.0",
            "matplotlib>=3.0.3",
            "pandas>=0.24.2"
                ],
      packages=find_packages()
      )