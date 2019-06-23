# -*- coding: utf-8 -*-
# :Project:   metapensiero.deform.semantic_ui -- Semantic-UI based Deform widgets
# :Created:   Fri 16 Feb 2018 17:21:24 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name="metapensiero.deform.semantic_ui",
    version=VERSION,
    url="https://gitlab.com/metapensiero/metapensiero.deform.semantic_ui.git",

    description="Replace standard Deform widgets with Semantic-UI equivalents",
    long_description=README + '\n\n' + CHANGES,

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        ],
    keywords="",

    packages=['metapensiero.deform.' + package
              for package in find_packages('src/metapensiero/deform')],
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.deform'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'setuptools',
        'deform',
        'chameleon',
    ],
    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'readme_renderer',
        ]
    },
)
