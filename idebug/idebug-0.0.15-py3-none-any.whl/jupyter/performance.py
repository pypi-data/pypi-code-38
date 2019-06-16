
#============================================================ IDE.
from jupyter.hydrogen import *
#============================================================ Project.
from idebug.performance import *
#============================================================ Python.
import time
#============================================================ Data-Science.




#============================================================
"""Initialize."""
#============================================================


#============================================================
"""Looper."""
#============================================================

def caller_func():
    loop = Looper(inspect.currentframe(), len=10, exp_runtime=1)
    pp.pprint(loop.__dict__)
    for e in range(1,3,1):
        time.sleep(5)
        loop.report('addi_info')

caller_func()



#============================================================
"""Function."""
#============================================================

def test_func():
    f = Function(inspect.currentframe()).report_init()
    time.sleep(3)
    f.report_fin()

test_func()
