#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

from setuptools import setup

# grab metadata without importing the module
metadata = {}
with open("lavacli/__about__.py", encoding="utf-8") as fp:
    exec(fp.read(), metadata)

# Setup the package
setup(
    name="lavacli",
    version=metadata["__version__"],
    description=metadata["__description__"],
    author=metadata["__author__"],
    author_email="remi.duraffort@linaro.org",
    license=metadata["__license__"],
    url=metadata["__url__"],
    python_requires=">=3.4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking",
    ],
    packages=["lavacli", "lavacli.commands"],
    entry_points={"console_scripts": ["lavacli = lavacli:main"]},
    install_requires=["jinja2", "PyYAML", "pyzmq", "requests"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=True,
)
