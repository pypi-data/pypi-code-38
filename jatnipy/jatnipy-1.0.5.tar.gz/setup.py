from setuptools import setup
import os

DISTNAME = 'jatnipy'
VERSION = '1.0.5'
DESCRIPTION = "Justin's, Andrea's, and Torbjörn's network inference package for Python"
with open('README.md') as f:
    a = f.read()
MAINTAINER = 'Justin Lin, Andreas Tjärnberg, Torbjörn Nordling'
MAINTAINER_EMAIL = 'justin.lin@nordlinglab.org,at145@nyu.edu,t@nordlinglab.org'
URL = 'https://bitbucket.org/temn/JATNIpy/'
DOWNLOAD_URL = 'https://pypi.org/project/jatnipy/#files'
LICENSE = 'LGPL'

setup(name=DISTNAME,
      version=VERSION,
      description=DESCRIPTION,
      url=URL,
      author=MAINTAINER,
      author_email=MAINTAINER_EMAIL,
      long_description = a,
      license=LICENSE,
      packages=['jatnipy','jatnipy/analyse','jatnipy/datastruct','jatnipy/Methods'],
      python_requires='>=3',
      install_requires=[
          'numpy',
          'py-ubjson',
          'scipy',
          'pandas',
          'prettytable',
          'matplotlib',
          'networkx',
          'scikit-learn',
          'glmnet_py',
          'requests',
          'cvxpy',
      ],
      zip_safe=False)
