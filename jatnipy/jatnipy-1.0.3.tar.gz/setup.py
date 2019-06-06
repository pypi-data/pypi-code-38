from setuptools import setup

long_description = "Justin's, Andrea's, and Torbjörn's network inference package for Python. We re-implemented GeneSPIDER toolbox in Python. Source code and documentation freely available at https://bitbucket.org/temn/JATNIpy/"

DISTNAME = 'jatnipy'
VERSION = '1.0.3'
DESCRIPTION = "Justin's, Andrea's, and Torbjörn's network inference package for Python"
# with open('README.rst') as f:
#     LONG_DESCRIPTION = f.read()
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
      license=LICENSE,
      long_description = long_description,
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
