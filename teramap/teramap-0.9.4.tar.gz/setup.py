#!/usr/bin/env python
import os
import re
import sys

from setuptools import find_packages, setup

# get version without importing
with open("teramap/__init__.py", "rb") as f:
    VERSION = str(re.search('__version__ = "(.+?)"', f.read().decode("utf-8")).group(1))

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")
    os.system("twine upload dist/teramap-{}.tar.gz".format(VERSION))
    message = "\nreleased [{version}](https://pypi.org/project/teramap/{version}/)"
    print(message.format(version=VERSION))
    sys.exit()

if sys.argv[-1] == "tag":
    release_files = [
        # explicitly add build files
        "teramap/static/teramap/maps.css",
        "teramap/static/teramap/maps.js",
        "teramap/static/teramap/maps.js.map",
        "teramap/static/teramap/teramap.css",
        "teramap/static/teramap/teramap.js",
        "teramap/static/teramap/teramap.js.map",
        "teramap/static/teramap/fieldwork.css",
        "teramap/static/teramap/fieldwork.js",
        "teramap/static/teramap/fieldwork.js.map",
        "teramap/__init__.py",
    ]
    # build javascript bundles
    os.system("npm run bundle")
    os.system("git add -f {}".format(" ".join(release_files)))
    os.system('git commit {} -m "Bump version to v{}"'.format(" ".join(release_files), VERSION))

    # create the tag
    os.system("git tag -a v{} -m 'tagging v{}'".format(VERSION, VERSION))
    os.system("git push --tags && git push origin master")
    sys.exit()


setup(
    name="teramap",
    version=VERSION,
    description="Shared mapping functionality for Zostera projects",
    author="Jan Pieter Waagmeester",
    author_email="jieter@zostera.nl",
    license="commercial",
    url="https://bitbucket.org/zostera/teramap",
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,  # declarations in MANIFEST.in
    install_requires=[],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
)
