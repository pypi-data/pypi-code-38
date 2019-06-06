import os
import angreal
from angreal import Git
from angreal import VirtualEnv

here = os.path.dirname(__file__)
requirements = os.path.join(here, '..', 'requirements.txt')


@angreal.command()
def init():
    """
    initialize a python project
    """

    # create our virtual environment and activate it for the rest of this run.

    angreal.warn('Creating virtual environment, this may take a moment')
    VirtualEnv(name='{{angreal.name}}', python='python3', requirements=requirements)
    angreal.win('Virtual environment {} created'.format('{{angreal.name}}'))

    # Initialize the git repo and push to the remote
    git = Git()
    git.init()
    git.add('.')
    git.commit('-m', 'Project initialized via angreal.')

    angreal.win('{{ angreal.name }} successfully created !')
    return
