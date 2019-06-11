#!/usr/bin/env python

from setuptools import setup, find_packages
import pkg_resources
import sys

try :
  import numpy, scipy
except ImportError :
  print('Software is irritating sometimes.\n\n'
        'Because of annoying but I suppose good reasons, numpy and scipy \n'
        'both have to be installed prior to installing this package. Please \n'
        'install them first and then try again.')
  sys.exit(1)

# https://packaging.python.org/guides/single-sourcing-package-version/
with open('de_toolkit/version.py') as f :
    exec(f.read())

setup(name='de_toolkit',
      version=__version__
      ,description='Suite of tools for working with count data'
      ,author='Adam Labadorf and the BU Bioinformatics Hub Team'
      ,author_email='labadorf@bu.edu'
      ,install_requires=[
          'docopt',
          'future',
          'jinja2',
          'numpy',
          'pandas',
          'patsy',
          'ply',
          'setuptools',
          'scipy',
          'scikit-learn',
          'statsmodels>=0.8.0',
          'terminaltables'
          ]
      ,packages=find_packages()
      ,package_data={'de_toolkit':['templates']}
      ,include_package_data=True
      ,entry_points={
        'console_scripts': [
          'detk=de_toolkit.common:main'
          ,'detk-norm=de_toolkit.norm:main'
          ,'detk-de=de_toolkit.de:main'
          ,'detk-enrich=de_toolkit.enrich:main'
          ,'detk-transform=de_toolkit.transform:main'
          ,'detk-filter=de_toolkit.filter:main'
          ,'detk-stats=de_toolkit.stats:main'
          ,'detk-outlier=de_toolkit.outlier:main'
          ,'detk-wrapr=de_toolkit.wrapr:main'
          ,'detk-report=de_toolkit.report:main'
          ,'detk-util=de_toolkit.util:main'
        ]
      }
      ,setup_requires=[
        'pytest-runner'
       ]
      ,tests_require=['pytest']
      ,url='https://bitbucket.org/bubioinformaticshub/de_toolkit'
      ,license='MIT'
      ,classifiers=[
        'Development Status :: 3 - Alpha'
        ,'Intended Audience :: Science/Research'
        ,'Environment :: Console'
        ,'License :: OSI Approved :: MIT License'
        ,'Programming Language :: Python :: 3'
        ,'Topic :: Scientific/Engineering :: Bio-Informatics'
      ]
      ,keywords=['bioinformatics','biology','sequencing','NGS']
      ,python_requires='~=3.3'
     )
