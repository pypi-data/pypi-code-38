# This file is part of hive, a distributed bug tracker
# Copyright (c) 2019 by Adam Hartz <hz@mit.edu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import subprocess

from setuptools import setup

from hive_bt import __version__ as HIVE_VERSION


def main():
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r") as f:
        requirements = f.read().split("\n")

    with open(os.path.join(os.path.dirname(__file__), "README"), "r") as f:
        readme = f.read()

    setup(
        name="hive_bt",
        version=HIVE_VERSION,
        author="Adam Hartz",
        author_email="hz@mit.edu",
        packages=["hive_bt", "hive_bt.web"],
        scripts=[],
        url="https://hz.mit.edu/hive",
        license="AGPLv3+",
        description="Hive is a distributed bug tracker.",
        long_description=readme,
        include_package_data=True,
        entry_points={"console_scripts": ["hive = hive_bt.cli:main"]},
        install_requires=requirements,
        package_dir={"hive_bt": "hive_bt"},
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Environment :: Console",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Software Development :: Bug Tracking",
        ],
    )


if __name__ == "__main__":
    main()
