#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Thu Nov 17 16:09:22 CET 2016
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Tests for the PAD Filelist database.
"""

import os
import bob.io.base.test_utils
from bob.pad.base.database import FileListPadDatabase


example_dir = os.path.realpath(bob.io.base.test_utils.datafile('.', __name__, 'data/example_filelist'))


def test_query():

    db = FileListPadDatabase(example_dir, 'test_padfilelist')
    assert len(db.groups()) == 3  # 3 groups (dev, eval, train)

    print(db.client_ids())
    # 5 client ids for real data of train, dev and eval sets (ignore all ids that are in attacks only)
    assert len(db.client_ids()) == 5
    assert len(db.client_ids(groups='train')) == 2  # 2 client ids for train
    assert len(db.client_ids(groups='dev')) == 2  # 2 client ids for dev
    assert len(db.client_ids(groups='eval')) == 1  # 2 client ids for eval

    assert len(db.objects(groups='train')) == 3  # 3 samples in the train set

    assert len(db.objects(groups='dev', purposes='real')) == 2  # 2 samples of real data in the dev set
    assert len(db.objects(groups='dev', purposes='attack')) == 1  # 1 attack in the dev set


def test_query_protocol():
    db = FileListPadDatabase(os.path.dirname(example_dir), 'test_padfilelist')
    p = 'example_filelist'

    assert len(db.groups(protocol=p)) == 3  # 3 groups (dev, eval, train)

    assert len(db.client_ids(protocol=p)) == 5  # 6 client ids for train, dev and eval
    assert len(db.client_ids(groups='train', protocol=p)) == 2  # 2 client ids for train
    assert len(db.client_ids(groups='dev', protocol=p)) == 2  # 2 client ids for dev
    assert len(db.client_ids(groups='eval', protocol=p)) == 1  # 2 client ids for eval

    assert len(db.objects(groups='train', protocol=p)) == 3  # 3 samples in the train set

    assert len(db.objects(groups='dev', purposes='real', protocol=p)) == 2  # 2 samples of real data in the dev set
    assert len(db.objects(groups='dev', purposes='attack', protocol=p)) == 1  # 1 attack in the dev set


def test_driver_api():
    from bob.db.base.script.dbmanage import main
    assert main(('pad_filelist clients --list-directory=%s --self-test' % example_dir).split()) == 0
    assert main(('pad_filelist dumplist --list-directory=%s --self-test' % example_dir).split()) == 0
    assert main(('pad_filelist dumplist --list-directory=%s --purpose=real --group=dev --self-test' % 
                 example_dir).split()) == 0
    assert main(('pad_filelist checkfiles --list-directory=%s --self-test' % example_dir).split()) == 0
