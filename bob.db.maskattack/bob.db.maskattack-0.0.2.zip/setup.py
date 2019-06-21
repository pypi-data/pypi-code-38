#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 21 Nov 08:21:19 CET 2016

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

setup(
    name='bob.db.maskattack',
    version=version,
    description="Bob Database interface for the 3DMAD database",
    keywords=['bob', 'database', 'mask'],
    url='http://gitlab.idiap.ch/heusch/bob.db.fargo',
    license='GPLv3',
    author='Guillaume Heusch',
    author_email='guillaume.heusch@idiap.ch',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,
 
    entry_points = {
      
        'console_scripts': [
          'make_sequences.py = bob.db.maskattack.scripts.make_color_videos:main'
        ],
        
        'bob.db': [
          'maskattack = bob.db.maskattack.driver:Interface',
        ],
    },

    classifiers=[
      'Framework :: Bob',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

    )
