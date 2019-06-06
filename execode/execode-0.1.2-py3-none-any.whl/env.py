# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import contextlib

from fsoopify import Path

from .runner import run_py
from .utils import find_pipenv_venv

@contextlib.contextmanager
def pipenv_context(cwd: str):
    venv = find_pipenv_venv(cwd)
    if not venv:
        raise FileNotFoundError(f'unable to find venv for {cwd}')

    activate_this_path = Path(venv) / 'Scripts' / 'activate_this.py'
    run_py(activate_this_path)
    yield
