import os


import angreal
from angreal import VirtualEnv
from angreal import Git


here = os.path.dirname(__file__)

pypirc = os.path.expanduser(os.path.join('~', '.pypirc'))
requirements = os.path.join(here, '..', 'requirements', 'dev.txt')

@angreal.command()
def init():
    """
    initialize a python project
    """


    # create our virtual environment and activate it for the rest of this run.

    angreal.warn('Virtual environment {} being created.'.format('{{angreal._cleaned_name}}'))
    VirtualEnv(name='{{angreal._cleaned_name}}', python='python3', requirements=requirements)
    angreal.win('Virtual environment {} created'.format('{{angreal._cleaned_name}}'))

    # Initialize the git repo
    git = Git()
    git.init()
    git.add('.')
    git.commit('-m', 'Project initialized via angreal.')

    angreal.win('{{ angreal._cleaned_name }} successfully created !')

    return
