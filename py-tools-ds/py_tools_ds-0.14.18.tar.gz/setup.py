#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("py_tools_ds/version.py") as version_file:
    exec(version_file.read(), version)

requirements = ['gdal', 'numpy', 'shapely', 'six', 'rasterio', 'pandas', 'geopandas',
                'scikit-image', 'pyproj', 'spectral', 'pyresample>=1.11.0']
setup_requirements = []  # TODO(danschef): put setup requirements (distutils extensions, etc.) here
test_requirements = requirements + ["coverage", "nose", "nose2", "nose-htmloutput", "rednose"]

setup(
    name='py_tools_ds',
    version=version['__version__'],
    description="A collection of Python tools by Daniel Scheffler.",
    long_description=readme + '\n\n' + history,
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    url='https://gitext.gfz-potsdam.de/danschef/py_tools_ds',
    packages=find_packages(),  # searches for packages with an __init__.py and returns them as properly formatted list
    package_dir={'py_tools_ds': 'py_tools_ds'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3 (GPLv3)",
    zip_safe=False,
    keywords='py_tools_ds',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements
)
