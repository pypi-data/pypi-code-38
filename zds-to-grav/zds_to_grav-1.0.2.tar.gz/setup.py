#!/usr/bin/env python

from setuptools import setup, find_packages

import zds_to_grav

setup(
    name="zds_to_grav",
    version=zds_to_grav.__version__,
    packages=find_packages(),
    author="Amaury Carrade",
    author_email="amaury@carrade.eu",
    description="Converts Zeste de Savoir articles to Grav",
    long_description=open("README.md").read(),
    install_requires=[
        "click >= 6",
        "requests",
        "path.py >= 2.19",
        "bs4",
        "awesome-slugify",
        "pyyaml",
    ],
    include_package_data=True,
    url="http://github.com/AmauryCarrade/zds-to-grav",
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": ["zds-to-grav = zds_to_grav:zds_to_grav"]},
    license="CeCILL-B",
)
