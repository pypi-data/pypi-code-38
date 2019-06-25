# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- a Simple Enough Markup
# :Created:   Wed 23 Nov 2016 09:14:23 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Arstecnica s.r.l.
# :Copyright: © 2018, 2019 Lele Gaifax
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
    name="metapensiero.markup.semtext",
    version=VERSION,
    url="https://gitlab.com/metapensiero/metapensiero.markup.semtext.git",

    description="a Simple Enough Markup",
    long_description=README + '\n\n' + CHANGES,
    long_description_content_type='text/x-rst',

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        ],
    keywords="",

    packages=['metapensiero.markup.' + package
              for package in find_packages('src/metapensiero/markup')],
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.markup'],

    install_requires=[
        'lxml',
        'setuptools',
        'sly',
    ],
    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'readme_renderer',
            'twine',
        ]
    },
)
