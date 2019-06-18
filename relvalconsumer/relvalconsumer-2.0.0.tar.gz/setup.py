# Copyright (C) Red Hat Inc.
#
# relvalconsumer is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

"""Setuptools script."""

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    """Pytest integration."""
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''
        self.test_suite = 'tests'

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args.split())
        sys.exit(errno)


# From: https://github.com/pypa/pypi-legacy/issues/148
# Produce rst-formatted long_description if pypandoc is available (to
# look nice on pypi), otherwise just use the Markdown-formatted one
try:
    import pypandoc
    longdesc = pypandoc.convert('README.md', 'rst')
except ImportError:
    longdesc = open('README.md').read()

# this is sloppy and wrong, see https://stackoverflow.com/a/4792601
# discussion, but should be okay for our purposes. the problem here
# is that if you run 'python3 setup.py install' with all the install
# requires in place, setuptools installs scripts from several of the
# deps to /usr/local/bin , overriding the system copies in /usr/bin.
# This seems to happen when the copy in /usr/bin is for Python 2 not
# Python 3 - e.g. because /usr/bin/fedmsg-logger is Python 2, if you
# do 'python3 setup.py install' here, due to the fedmsg dep, you get
# a /usr/local/bin/fedmsg-logger which is Python 3...we want to be
# able to avoid this, so hack up a 'no deps'
if "--nodeps" in sys.argv:
    installreqs = []
    sys.argv.remove("--nodeps")
else:
    installreqs = open('install.requires').read().splitlines()

setup(
    name="relvalconsumer",
    version="2.0.0",
    py_modules=['relvalconsumer'],
    author="Adam Williamson",
    author_email="awilliam@redhat.com",
    description=("Fedora QA wiki release validation event fedora-messaging consumer"),
    license="GPLv3+",
    keywords="fedora qa mediawiki validation",
    url="https://pagure.io/fedora-qa/relvalconsumer",
    install_requires=installreqs,
    tests_require=open('tests.requires').read().splitlines(),
    cmdclass={'test': PyTest},
    long_description=longdesc,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)

# vim: set textwidth=120 ts=8 et sw=4:
