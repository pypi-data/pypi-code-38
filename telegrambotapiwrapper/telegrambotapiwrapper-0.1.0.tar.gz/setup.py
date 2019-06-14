import os

from codecs import open

import setuptools
from distutils.core import setup
here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(
        os.path.join(here, 'telegrambotapiwrapper', '__init__.py'), 'r',
        'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    python_requires='>=3.7',
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=about['__url__'],
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
