import codecs
import os
import re

from setuptools import setup, find_packages

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

setup(
  name = 'nao',
  packages = find_packages(),
  version = '0.2.1',
  description = 'Intelligent data manipulation tools',
  author = 'Szabolcs Blaga',
  author_email = 'szabolcs.blaga@gmail.com',
  url = 'https://github.com/blagasz/nao',
  download_url = 'https://github.com/blagasz/nao/tarball/0.1',
  license = 'GPL',
  install_requires=[
    'PyYAML',
    # 'numpy==1.11.1',
    # 'pandas==0.18.1',  # for datetime conversion and distinct
    # 'SQLAlchemy',
  ],
  keywords = ['data', 'yaml', 'multilingual', 'multivalue', 'config', 'flask', 'sqlalchemy'],
  classifiers = [],
)