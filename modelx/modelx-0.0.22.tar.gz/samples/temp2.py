import sys
import pathlib
from modelx.core.project import read_model, write_model


from lifelib.projects.ifrs17sim import ifrs17sim
# from lifelib.projects.simplelife import simplelife

sys.path.insert(0, str(pathlib.Path(ifrs17sim.__file__).parent))

path_ = str(pathlib.Path(__file__).parent / 'temp' / 'ifrs17simdir')

if True:
    m = ifrs17sim.build(False)
    m.hoge = "hoge"
    m.foo = 1
    m.bar = m.OuterProj
    m.OuterProj.new_cells(name="baz", formula=lambda x: 3 * x)
    # m.OuterProj.baz.set_property("allow_none", True)
    m.none = None
    m.true = True

    # write_model(m, path_)
    m.write(path_)

import os

if True:
    os.chdir(str(path_))
    m = read_model(path_)

