""" Provide highlevel access to calculator.calculate """
from .calculate import calculate_socket, calc_dirname
from hilde.settings import Settings
from hilde.helpers.utils import talk


def run():
    """ loader for hilde workflows:
            - phonopy
            - md """

    # load settings
    settings = Settings()

    if "phonopy" in settings:
        from hilde.phonopy import run_phonopy

        talk("launch phonoy workflow")

        run_phonopy()

    elif "md" in settings:
        from hilde.molecular_dynamics import run_md

        talk("launch MD workflow")

        run_md()
