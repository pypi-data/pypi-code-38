#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup
from lexed import __version__

build_number = os.getenv('TRAVIS_BUILD_NUMBER', '')
branch = os.getenv('TRAVIS_BRANCH', '')
travis = any((build_number, branch,))
version = __version__.split('.')
develop_status = '4 - Beta'
url = 'http://lexycore.github.io/lexed'

if travis:
    version = version[0:3]
    if branch == 'master':
        develop_status = '5 - Production/Stable'
        version.append(build_number)
    else:
        version.append('{}{}'.format('dev' if branch == 'develop' else branch, build_number))
else:
    if len(version) < 4:
        version.append('local')

version = '.'.join(version)
if travis:
    with open('lexed/__init__.py', 'w', encoding="utf-8") as f:
        f.write("__version__ = '{}'".format(version))

try:
    import pypandoc

    print("Converting README...")
    long_description = pypandoc.convert('README.md', 'rst')
    if branch:
        long_description = long_description.replace('lexed.svg?branch=master', 'lexed.svg?branch={}'.format(branch))

except (IOError, ImportError, OSError):
    print("Pandoc not found. Long_description conversion failure.")
    with open('README.md', encoding="utf-8") as f:
        long_description = f.read()
else:
    print("Saving README.rst...")
    try:
        if len(long_description) > 0:
            with open('README.rst', 'w', encoding="utf-8") as f:
                f.write(long_description)
            if travis:
                os.remove('README.md')
    except:
        print("  failed!")

setup(
    name='lexed',
    version=version,
    description='LexEd - console python editor',
    license='MIT',
    author='Alexander Kovalev',
    author_email='ak@alkov.pro',
    url=url,
    long_description=long_description,
    download_url='https://github.com/lexycore/lexed.git',
    entry_points={'console_scripts': ['lexed=lexed.__main__:main']},
    classifiers=[
        f'Development Status :: {develop_status}',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=[
        'development',
        'editor',
    ],
    packages=[
        'lexed',
    ],
    setup_requires=[
        'wheel',
        'pypandoc',
    ],
    tests_require=[
        'pytest',
    ],
    install_requires=[
    ],
    package_data={
        '': [
            '../LICENSE',
        ],
    },
)
