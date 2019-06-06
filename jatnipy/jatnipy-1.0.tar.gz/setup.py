from setuptools import setup

DISTNAME = 'jatnipy'
VERSION = '1.0'
DESCRIPTION = "Justin's, Andrea's, and Torbjörn's network inference package for Python"
# with open('README.rst') as f:
#     LONG_DESCRIPTION = f.read()
MAINTAINER = 'Justin Lin'
MAINTAINER_EMAIL = 'justin.lin@nordlinglab.org'
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
      packages=['jatnipy'],
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
