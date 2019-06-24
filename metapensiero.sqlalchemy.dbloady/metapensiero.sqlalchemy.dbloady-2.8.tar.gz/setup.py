# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   ven  1 gen 2016, 16.19.54, CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019 Lele Gaifax
#

from io import open
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
    name="metapensiero.sqlalchemy.dbloady",
    version=VERSION,
    url="https://gitlab.com/metapensiero/metapensiero.sqlalchemy.dbloady.git",

    description="YAML based data loader",
    long_description=README + u'\n\n' + CHANGES,
    long_description_content_type='text/x-rst',

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
    keywords='',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.sqlalchemy'],

    install_requires=[
        'progressbar2',
        'ruamel.yaml',
        'setuptools',
        'sqlalchemy',
    ],
    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'readme_renderer',
            'twine',
        ]
    },

    entry_points="""\
    [console_scripts]
    dbdumpy = metapensiero.sqlalchemy.dbloady.dump:main
    dbloady = metapensiero.sqlalchemy.dbloady.load:main
    """,
)
