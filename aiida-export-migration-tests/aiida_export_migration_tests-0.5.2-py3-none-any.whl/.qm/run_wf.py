# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################


import sys
import os

from aiida.common.example_helpers import test_and_get_code
from aiida.work import run
from aiida.orm import DataFactory
from aiida.orm.group import Group

from wf import TestWorkChain
################################################################

StructureData = DataFactory('structure')

try:
    codename = sys.argv[1]
except IndexError:
    codename = None

code = test_and_get_code(codename, expected_code_type='quantumespresso.pw')

alat = 4.  # angstrom
cell = [[alat, 0., 0., ],
        [0., alat, 0., ],
        [0., 0., alat, ],
]

# BaTiO3 cubic structure
s = StructureData(cell=cell)
s.append_atom(position=(0., 0., 0.), symbols=['Ba'])
s.append_atom(position=(alat / 2., alat / 2., alat / 2.), symbols=['Ti'])
s.append_atom(position=(alat / 2., alat / 2., 0.), symbols=['O'])
s.append_atom(position=(alat / 2., 0., alat / 2.), symbols=['O'])
s.append_atom(position=(0., alat / 2., alat / 2.), symbols=['O'])

g = Group.create(name="input_group")
g.add_nodes(s.store())

w = TestWorkChain
run(w, structure=s.store(), code=code)
