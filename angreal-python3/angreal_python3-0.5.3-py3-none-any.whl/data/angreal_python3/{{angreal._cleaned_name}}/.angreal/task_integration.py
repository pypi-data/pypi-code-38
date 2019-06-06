import angreal
import os
import subprocess
from angreal import venv_required

here = os.path.realpath(os.path.dirname(__file__))
cwd = os.getcwd()


@angreal.command()
@venv_required('{{ angreal._cleaned_name }}')
def angreal_cmd():
    """
    run package tests
    """
    os.chdir(os.path.join(here, '..'))

    subprocess.run('pytest tests/integration/ -s -vvv ', shell=True)
    return