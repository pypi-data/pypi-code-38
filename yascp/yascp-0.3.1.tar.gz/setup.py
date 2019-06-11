import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='yascp',
      version='0.3.1',
      description='Yet Another Simple Configuration Parser for \
      INI-style configuration files.',
      url='https://pypi.python.org/pypi/yascp/',
      author='Miroslaw Janiewicz',
      author_email='miroslaw.janiewicz@gmail.com',
      license='MIT',
      packages=['yascp'],
      zip_safe=True,
      long_description=read('README'),
      keywords=['configuration', 'parse', 'parser', 'ini', 'yascp'],
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console"],
      scripts=['yascp/yascp_parser.py'],
      install_requires=['future']
      )
