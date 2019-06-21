#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Thu Oct 09 11:27:27 CEST 2014
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
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

"""A few checks on the protocols of the Near-Infrared and Visible-Light (NIVL) Dataset
"""

import bob.db.pericrosseye

""" Defining protocols. Yes, they are static """
PROTOCOLS = ('cross-eye-VIS-NIR-split1', \
             'cross-eye-VIS-NIR-split2', \
             'cross-eye-VIS-NIR-split3', \
             'cross-eye-VIS-NIR-split4', \
             'cross-eye-VIS-NIR-split5')

GROUPS = ('world', 'dev', 'eval')

PURPOSES = ('train', 'enroll', 'probe')


def test00_protocols_clients():
    # testing protocols

    db = bob.db.pericrosseye.Database()
    for p in db.protocols():
        assert len(db.model_ids(protocol=p, groups="world")) == 20
        assert len(db.model_ids(protocol=p, groups="dev")) == 10
        assert len(db.model_ids(protocol=p, groups="eval")) == 10


def test01_protocols_purposes_groups():
    # testing protocols

    # possible_protocols = bob.db.pericrosseye.Database().protocols()
    # for p in possible_protocols:
    # assert p  in PROTOCOLS

    # testing purposes
    possible_purposes = bob.db.pericrosseye.Database().purposes()
    for p in possible_purposes:
        assert p in PURPOSES

    # testing GROUPS
    possible_groups = bob.db.pericrosseye.Database().groups()
    for p in possible_groups:
        assert p in GROUPS


def test02_objects():

    db = bob.db.pericrosseye.Database()
    for p in db.protocols():
        assert len(db.objects(protocol=p, groups="world")) == 16 * 20
        assert len(db.objects(protocol=p, groups="dev")) == 10 + 8 * 10
        assert len(db.objects(protocol=p, groups="eval")) == 10 + 8 *10

        assert len(db.objects(protocol=p, groups="dev", purposes=("enroll",))) == 10
        assert len(db.objects(protocol=p, groups="dev", purposes=("probe",))) == 8*10

        assert len(db.objects(protocol=p, groups="eval", purposes=("enroll",))) == 10
        assert len(db.objects(protocol=p, groups="eval", purposes=("probe",))) == 8*10
