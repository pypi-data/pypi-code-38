"""
A package for adding enhancements to text editors in a cross-platform, cross-editor manner.
https://github.com/wilvk/tide

See:
https://github.com/wilvk/tide

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

  name = 'tide',

  version = '0.1.8',

  description = 'From text editor to Integrated Development Environment. This allows you to use a yaml config and some scripting to deliver cross-platform, cross-editor plugins.',

  author = 'Willem van Ketwich',
  author_email = 'willvk@gmail.com',

  license = 'MIT',

  python_requires='>=3.4',

  url = 'https://github.com/wilvk/tide',

  download_url = 'https://github.com/wilvk/tide/archive/0.1.tar.gz',

  long_description=long_description,

  classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'Topic :: Software Development',
      'Topic :: Text Editors',
      'Topic :: Text Processing',
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
      'Intended Audience :: Information Technology',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
  ],

  keywords = ['editor', 'configuration'],

  install_requires = [
      'jinja2',
      'markupsafe',
      'pexpect',
      'ptyprocess',
      'pyyaml',
      'six',
      'yamlreader'
  ],

  packages = find_packages(),

  extras_require={
      'dev': [],
      'test': [ 'nose' ],
  },

  entry_points={
      'console_scripts': [
          'tide=tide:main',
      ],
  },

)
