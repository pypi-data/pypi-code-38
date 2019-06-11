import os


import angreal
from angreal import VirtualEnv, venv_required


here = os.path.dirname(__file__)
requirements = os.path.join(here, '..', 'requirements', 'requirements.txt')
requirements_dev = os.path.join(here, '..', 'requirements', 'dev.txt')


@angreal.command()
@angreal.option('--no_dev', is_flag=True, help='Do not setup a dev environment.')
@venv_required('{{angreal._cleaned_name}}')
def angreal_cmd(no_dev):
    """
    update/create the {{angreal.name}} environment.
    """
    # create our virtual environment and activate it for the rest of this run.
    reqs = requirements_dev
    if no_dev:
        reqs = requirements

    VirtualEnv(name='{{angreal._cleaned_name}}', python='python3', requirements=reqs)
    angreal.win('Virtual environment {} updated.'.format('{{angreal._cleaned_name}}'))
    return
