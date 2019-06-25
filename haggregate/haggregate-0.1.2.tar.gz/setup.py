#!/usr/bin/env python

import os
import re

from setuptools import Extension, find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=7.0,<8", "htimeseries>=1.1,<2"]

setup_requirements = ["cython>=0.29,<0.30"]

test_requirements = []


def use_cython():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    regularize_pyx = os.path.join(base_dir, "haggregate", "regularize.pyx")
    regularize_pyx_exists = os.path.exists(regularize_pyx)
    regularize_c = os.path.join(base_dir, "haggregate", "regularize.c")
    regularize_c_exists = os.path.exists(regularize_c)

    if (not regularize_pyx_exists) and (not regularize_c_exists):
        raise Exception("Neither {} nor {} exists".format(regularize_pyx, regularize_c))

    return (not regularize_c_exists) or (
        regularize_pyx_exists
        and os.path.getmtime(regularize_pyx) > os.path.getmtime(regularize_c)
    )


if use_cython():
    import numpy
    from Cython.Build import cythonize

    ext_modules = cythonize("haggregate/regularize.pyx")
    include_dirs = [numpy.get_include()]
else:
    ext_modules = [Extension("haggregate.regularize", ["haggregate/regularize.c"])]
    include_dirs = None


def get_version():
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    init_py_path = os.path.join(scriptdir, "haggregate", "__init__.py")
    with open(init_py_path) as f:
        return re.search(r'^__version__ = "(.*?)"$', f.read(), re.MULTILINE).group(1)


setup(
    ext_modules=ext_modules,
    include_dirs=include_dirs,
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Aggregates htimeseries to larger steps",
    entry_points={"console_scripts": ["haggregate=haggregate.cli:main"]},
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="haggregate",
    name="haggregate",
    packages=find_packages(include=["haggregate"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/openmeteo/haggregate",
    version=get_version(),
    zip_safe=False,
)
