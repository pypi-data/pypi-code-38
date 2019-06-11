#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from distutils.core import setup
import os.path

with open(os.path.join(os.path.dirname(__file__), 'README')) as f:
    description = f.read()

setup(name="pgbouncer",
      version="0.0.9",
      description="Fixture to bring up temporary pgbouncer instance.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/python-pgbouncer",
      packages=['pgbouncer'],
      package_dir={'': '.'},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          ],
      install_requires=[
          'fixtures',
          'psycopg2',
          ],
      extras_require=dict(
          test=[
              'postgresfixture',
              'testscenarios',
              'testtools',
              ]
          ),
      )
