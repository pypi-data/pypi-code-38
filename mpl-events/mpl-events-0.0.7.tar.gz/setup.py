# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup, find_packages


NAME = 'mpl-events'
ROOT_DIR = pathlib.Path(__file__).parent
PYTHON_REQUIRES = '>=3.6, <4'


def _get_version():
    about = {}
    ver_mod = ROOT_DIR / 'mpl_events' / '__version__.py'
    with ver_mod.open() as f:
        exec(f.read(), about)
    return about['__version__']


def _get_long_description():
    readme = ROOT_DIR / 'README.md'
    with readme.open(encoding='utf-8') as f:
        return '\n' + f.read()


setup(
    name=NAME,
    version=_get_version(),
    python_requires=PYTHON_REQUIRES,
    install_requires=['matplotlib >=2.0,<3.2'],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    url='https://github.com/espdev/mpl-events',
    license='MIT',
    author='Eugene Prilepin',
    author_email='esp.home@gmail.com',
    description='A tiny library for simple and convenient matplotlib event handling',
    long_description=_get_long_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
