

import codecs
import os
import re

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# long_description = read('README.rst')

# setup(
#   name = 'nao',
#   packages = ['nao'],  # find_packages(),
#   version = '0.2.1',
#   description = 'Intelligent data manipulation tools',
#   author = '',
#   author_email = 'szabolcs.blaga@gmail.com',
#   url = 'https://github.com/blagasz/nao',
#   download_url = 'https://github.com/blagasz/nao/tarball/0.1',
#   license = 'GPL',
#   install_requires=[
#     'PyYAML',
#     # 'numpy==1.11.1',
#     # 'pandas==0.18.1',  # for datetime conversion and distinct
#     # 'SQLAlchemy',
#   ],
#   keywords = ['data', 'yaml', 'multilingual', 'multivalue', 'config', 'flask', 'sqlalchemy'],
#   classifiers = [],
# )

# based on https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56


from distutils.core import setup

setup(
  name = 'nao',
  packages = ['nao', 'nao.ext'],
  version = find_version("nao", "__init__.py"),
  license='GPL',
  description = 'Intelligent data manipulation tools',
  author = 'Szabolcs Blága',
  author_email = 'szabolcs.blaga@gmail.com',
  url = 'https://github.com/blagasz/nao',
  download_url = 'https://github.com/blagasz/nao/archive/v0.2.zip',
  keywords = ['data', 'yaml', 'multilingual', 'multivalue', 'config', 'flask', 'sqlalchemy'],
  setup_requires=['wheel'],
  install_requires=[
    'PyYAML',
    # 'numpy==1.11.1',
    # 'pandas==0.18.1',  # for datetime conversion and distinct
    # 'SQLAlchemy',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Utilities',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)