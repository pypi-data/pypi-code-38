""" handling restarts of tasks and workflows """
import subprocess as sp
from hilde.settings import Settings


def restart(settings=None, verbose=True):
    """ restart a job according to the restart instructions in the settings """

    if settings is None:
        settings = Settings()

    if "restart" in settings:
       if verbose:
            print(f"Restart task with {settings.restart.command}")
       sp.run(settings.restart.command.split(), stderr=sp.STDOUT)
       return True
    else:
        if verbose:
            print("Task not completed, please inspect and rerun.")
        return False
