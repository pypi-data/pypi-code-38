'''
PyPi upload procedure

1. Install twine: 
      pip install twine

2. Build and package code: 
      python setup.py sdist bdist_wheel
   Typically pip will install this version but will fall back to the source distribution if needed.
    - sdist: creates a source distribution 
    - bdist_wheel: creates a built distribution. 

3. Test upload to TestPyPi server:
      twine upload --repository-url https://test.pypi.org/legacy/ dist/* (if dist only contains latest distribution packages)
        or
      twine upload --repository-url https://test.pypi.org/legacy/ dist/osensapy-0.1.5* (replace with current version number)

4. Verify by installing library from TestPyPi:
      pip install --index-url https://test.pypi.org/simple/ osensapy

5. Upload to actual PyPi:
      twine upload dist/* (if dist only contains latest distribution packages)
        or
      twine upload dist/osensapy-0.1.5* (replace with current version number)  
'''

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

# Get the long description from the README file
with open('README.md', 'r') as f:
  long_description = f.read()

setup(
  # name: Name of project - this will be how the project is listed on PyPI
  name = 'osensapy',
  
  # packages: this must be the same as the name
  packages = ['osensapy'], # Can manually include packages
  # packages = find_packages(exclude=[]), # Or can automatically find packages (use exclude to omit packages not intended for release/install)
  
  # install_requires: specify what dependencies a project minimally needs to run
  install_requires = ['numpy', 'pyserial'],
  
  # python_requires: if project only runs on certain Python versions, specify this here
  python_requires = '>=2.6',		# requires Python 3+
  ##	python_requires = '~=3.3',		requires Python 3.3 and up, not willing to commit to Python 4 support yet
  ##	python_requires = '>=2.6, !=3.0.*, <4'	requires Python 2.6, 2.7, and all versions of Python 3 starting with 3.1
  
  # version: suggested versioning scheme
  #		1.2.0.dev1		development release
  #		1.2.0a1			alpha release
  #		1.2.0b1			beta release
  #		1.2.0rc1		release candidate
  #		1.2.0			final release
  #		1.2.0post1		post release
  version = '0.1.5',
  
  # description: short description of the project
  description = 'OSENSA Python library',
  
  # long_description: longer description of the project
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  
  # author: provides details of author
  author = 'OSENSA Innovations',
  author_email = 'cng@osensa.com',
  
  # license: provide type of license you are using
  license='MIT',
  
  # url: homepage 
  
  # keywords: list of keywords that describe this project
  keywords = [], # arbitrary keywords
  
  # classifiers: list of classifiers to categorize project. See full listing here: https://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers = [],

)