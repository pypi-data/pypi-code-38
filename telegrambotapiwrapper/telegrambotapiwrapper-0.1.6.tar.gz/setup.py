import os

from codecs import open

import setuptools
from distutils.core import setup

__title__ = 'telegrambotapiwrapper'
__description__ = 'Python Telegram Bot Api Wrapper.'
__url__ = 'https://github.com/pynista/telegrambotapiwrapper'
__version__ = '0.1.6'
__author__ = 'Dzmitry Maliuzhenets'
__author_email__ = 'dzmitrymaliuzhenets@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Dzmitry Maliuzhenets'

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    python_requires='>=3.7',
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=readme,
    long_description_content_type='text/markdown',
    url=__url__,
    packages=setuptools.find_packages(),
    keywords='telegram api bot wrapper',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
    ],
)
