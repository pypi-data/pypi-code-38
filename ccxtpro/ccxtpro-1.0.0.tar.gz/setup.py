# prefer setuptools over distutils
from setuptools import setup, find_packages

# use a consistent encoding
from codecs import open
from os import path
import json

here = path.abspath(path.dirname(__file__))
root = path.dirname(here)

readme = path.join(here, 'README.md')
package_json = path.join(here, 'package.json')

# a workaround when installing locally from git repository with pip install -e .
if not path.isfile(package_json):
    package_json = path.join(root, 'package.json')

# long description from README file
with open(readme, encoding='utf-8') as f:
    long_description = f.read()

# version number and all other params from package.json
with open(package_json, encoding='utf-8') as f:
    package = json.load(f)

setup(

    name='ccxtpro',
    version=package['version'],

    description=package['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',

    url=package['homepage'],

    author=package['author']['name'],
    author_email=package['author']['email'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: JavaScript',
        'Programming Language :: PHP',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ],

    packages=find_packages()
)
