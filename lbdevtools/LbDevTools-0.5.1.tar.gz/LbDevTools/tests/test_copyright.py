###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import print_function

from os.path import join, dirname, splitext

import LbDevTools.CopyrightCheck as C


DATA_DIR = join(dirname(__file__), 'data')


def test_is_script():
    assert C.is_script(join(DATA_DIR, 'a_script'))
    assert not C.is_script(join(DATA_DIR, 'not_a_script'))


def test_to_check():
    for to_check, name in ((True, 'a_script'),
                           (False, 'not_a_script'),
                           (True, 'source.py'),
                           (True, 'source.cpp'),
                           (True, 'source.xml'),
                           (False, '.')):
        assert C.to_check(join(DATA_DIR, name)) is to_check


def test_has_copyright():
    assert C.has_copyright(splitext(__file__)[0] + '.py')
    assert not C.has_copyright(join(DATA_DIR, 'a_script'))
