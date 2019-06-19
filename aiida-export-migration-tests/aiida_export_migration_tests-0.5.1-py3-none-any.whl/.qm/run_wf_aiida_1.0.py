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

from aiida.engine import run
from aiida.plugins.factories import DataFactory
from aiida.orm import Group
from aiida.orm import Code

from wf_aiida_1.0 import TestWorkChain
################################################################

StructureData = DataFactory('structure')

try:
    codename = sys.argv[1]
except IndexError:
    codename = None

if not codename:
    print ("Please provide a valid codename")
    sys.exit(1)
code = Code.get_from_string(codename)

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

g = Group(name="input_group").store()
g.add_nodes(s.store())

w = TestWorkChain
run(w, structure=s.store(), code=code)
