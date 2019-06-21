#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from nose.plugins.skip import SkipTest

import bob.bio.base
from bob.bio.base.test.utils import db_available
from bob.bio.base.test.test_database_implementations import check_database_zt
from bob.bio.face.test.test_databases import _check_annotations
import pkg_resources


@db_available('youtube')
def test_youtube():
    database = bob.bio.base.load_resource('youtube', 'database', preferred_package='bob.bio.video')
    try:
        check_database_zt(database, training_depends=True, models_depend=True)
    except IOError as e:
        raise SkipTest(
            "The database could not be queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)
    try:
        _check_annotations(database, limit_files=1000, topleft=True, framed=True)
    except IOError as e:
        raise SkipTest(
            "The annotations could not be queried; probably the annotation files are missing. Here is the error: '%s'" % e)


@db_available('mobio')
def test_mobio():
    database = bob.bio.base.load_resource('mobio', 'database', preferred_package='bob.bio.video')
    try:
        check_database_zt(database, models_depend=True)
    except IOError as e:
        raise SkipTest(
            "The database could not be queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)


@db_available('youtube')
def test_youtube_load_method():
    """
    Test the load method of the YoutubeBioFile class.
    """

    database = bob.bio.base.load_resource('youtube', 'database', preferred_package='bob.bio.video')

    try:

        youtube_bio_file = database.all_files()[0]

    except IOError as e:

        raise SkipTest(
            "The database could not be queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)

    directory = pkg_resources.resource_filename('bob.bio.video', 'test/data')

    frame_container = youtube_bio_file.load(directory=directory, extension=".jpg")

    assert (len(frame_container)==2)
