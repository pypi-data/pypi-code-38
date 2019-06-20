from setuptools import setup, find_packages
import os
import sys
import textwrap
import warnings
import urllib

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

with open('VERSION', 'r') as f_ver:
    VERSION = f_ver.read()

if sys.version_info[:2] < (2, 7):
    raise RuntimeError("Python version 2.7 required.")

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='watson_machine_learning_client_V4',
    version=VERSION,
    author='IBM',
    author_email='svagaral@in.ibm.com, nagiredd@in.ibm.com, kamigupt@in.ibm.com',
    description='Watson Machine Learning API Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD',
    classifiers=['Development Status :: 4 - Beta',
                 'Natural Language :: English',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX :: Linux',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Information Technology',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Internet'],
    keywords=["watson", "machine learning", "IBM", "Bluemix", "client", "API", "IBM Cloud"],
    url='http://wml-api-pyclient-v4.mybluemix.net',
    packages=find_packages(),
    install_requires=['requests',
                      'urllib3',
                      'pandas',
                      'certifi',
                      'tqdm',
                      'lomond',
                      'tabulate',
                      'ibm-cos-sdk'],
    include_package_data=True
)
