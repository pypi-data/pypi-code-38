# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

def run_py():
    import sys
    import os

    sys.argv.pop(0) # current script name
    if not sys.argv:
        raise RuntimeError('run-py require at least python script path as arguments.')
    target_path = sys.argv[0] # target script path

    from execode import run_py as rp
    rp(target_path)

def run_pym():
    import sys
    import os

    sys.argv.pop(0) # current script name
    if not sys.argv:
        raise RuntimeError('run-pym require at least python package path as arguments.')
    target_path = sys.argv[0] # target script path
    if not target_path.endswith('__main__.py'):
        target_path = os.path.join(target_path, '__main__.py')
        sys.argv[0] = target_path

    from execode import run_py_m as rpm
    rpm(target_path)

def pipenv_run_py():
    import sys
    import os

    if len(sys.argv) < 2:
        raise RuntimeError('pipenv-run-py require at least python script path as arguments.')
    target_path = sys.argv[1] # target script path

    from execode import pipenv_context
    with pipenv_context(os.path.dirname(target_path)):
        run_py()

def pipenv_run_pym():
    import sys
    import os

    if len(sys.argv) < 2:
        raise RuntimeError('pipenv-run-pym require at least python package path as arguments.')
    target_path = sys.argv[1] # target script path

    from execode import pipenv_context
    with pipenv_context(os.path.dirname(target_path)):
        run_pym()
