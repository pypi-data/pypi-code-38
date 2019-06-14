# -*- coding: utf-8 -*-

from codecs import open
from os.path import join, abspath, dirname

from setuptools import setup

CWD = abspath(dirname(__file__))
PACKAGE_NAME='cistatus'

# Get the long description from the README file
with open(join(CWD, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get version
CWD = abspath(dirname(__file__))
VERSION_PATH = join(CWD, PACKAGE_NAME, 'version.py')
exec(compile(open(VERSION_PATH).read(), VERSION_PATH, 'exec'))

with open(join(CWD, 'requirements.txt'), encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

CLASSIFIERS='''
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: Information Technology
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Topic :: Software Development :: Libraries
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Topic :: Utilities
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Operating System :: POSIX :: Other
'''.strip().splitlines()

setup(name=PACKAGE_NAME,
      version=VERSION,
      description='CI Tool for adding status check results for individual components',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=CLASSIFIERS,
      url='https://github.com/salabs/cistatus',
      author='Jani Mikkonen',
      author_email='jani.mikkonen@gmail.com',
      license='APACHE',
      packages=['cistatus'],
      install_requires=REQUIREMENTS,
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'cistatus = cistatus.cli:main',
          ],
      })
