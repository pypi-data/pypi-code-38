# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import contextlib

from fsoopify import Path

from .runner import run_py

@contextlib.contextmanager
def pipenv_context(pipfile_path):
    from pipenv.project import Project
    proj = Project(chdir=False)
    proj._pipfile_location = pipfile_path
    activate_this_path = Path(proj.virtualenv_location) / 'Scripts' / 'activate_this.py'
    run_py(activate_this_path)
    yield
