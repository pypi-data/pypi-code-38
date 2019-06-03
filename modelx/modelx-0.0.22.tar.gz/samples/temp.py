import modelx as mx

import sys
import pathlib
from modelx.core.project import read_model, write_model


# from lifelib.projects.ifrs17sim import ifrs17sim
# from lifelib.projects.simplelife import simplelife

# sys.path.insert(0, str(pathlib.Path(simplelife.__file__).parent))

# m = simplelife.build()
# m.hoge = "hoge"
# m.foo = 1
# m.bar = m.OuterProj
# m.OuterProj.new_cells(name="baz", formula=lambda x: 3 * x)
# # m.OuterProj.baz.set_property("allow_none", True)
# m.none = None
# m.true = True

path_ = str(pathlib.Path(__file__).parent / 'temp' / "testdir")

import os

os.chdir(str(pathlib.Path(__file__).parent / 'temp'))

if True:

    m = mx.new_model(name="xlsmpl")

    m.allow_none = True

    s = m.new_space(name='Space1')

    policydata = s.new_space_from_excel(
        book="input.xlsx",
        range_='B7:O307',
        sheet='PolicyData',
        name='PolicyData',
        names_row=0,
        param_cols=[0],
        space_param_order=[0],
        cells_param_order=[])

    write_model(m, path_)

os.chdir(str(pathlib.Path(__file__).parent / 'temp' / 'testdir'))

model = read_model(path_)
