import os
from setuptools import setup
import sys

requires = ['bin-parser==1.0.1']

# Python 2.6 does not include the argparse module.
try:
    import argparse
except ImportError:
    requires.append('argparse')

# This is quite the hack, but we don't want to import our package from here
# since that's recipe for disaster (it might have some uninstalled
# dependencies, or we might import another already installed version).
distmeta = {}
for line in open(os.path.join('python', '__init__.py')):
    try:
        field, value = (x.strip() for x in line.split('='))
    except ValueError:
        continue
    if field == '__version_info__':
        value = value.strip('[]()')
        value = '.'.join(x.strip(' \'"') for x in value.split(','))
    else:
        value = value.strip('\'"')
    distmeta[field] = value

#try:
#    with open('README.md') as readme:
#        long_description = readme.read()
#except IOError:
long_description = 'See ' + distmeta['__homepage__']

setup(
    name='fam-parser',
    version=distmeta['__version_info__'],
    description='FAM file parser',
    long_description=long_description,
    author=distmeta['__author__'],
    author_email=distmeta['__contact__'],
    url=distmeta['__homepage__'],
    license='MIT License',
    platforms=['any'],
    packages=['fam_parser'],
    install_requires=requires,
    package_dir={'fam_parser': 'python'},
    package_data={'fam_parser': ['structure.yml', 'types.yml']},
    entry_points={'console_scripts': ['fam_parser = fam_parser.cli:main']}
)
