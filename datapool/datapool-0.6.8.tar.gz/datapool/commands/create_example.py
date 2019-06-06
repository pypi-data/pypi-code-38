import shutil
from os.path import abspath, exists, join

from ..landing_zone import LandingZone, disable_write
from ..utils import here


def create_example(development_landing_zone, reset, print_ok, print_err):
    """creates local example landing zone serving examples for the initial setup.
    """

    print_ok("- setup example landing zone")

    if exists(development_landing_zone):
        if not reset:
            print_err("  - folder {} already exists.".format(development_landing_zone))
            return 1
        else:
            try:
                shutil.rmtree(development_landing_zone)
            except Exception as e:
                print_err(
                    "  - could not delete folder {}".format(
                        abspath(development_landing_zone)
                    )
                )
                print_err("  - error message is: {}".format(e))
                return 1

    lz = LandingZone(development_landing_zone)
    source = join(here(), "..", "instance", "default_initial_landing_zone")
    shutil.copytree(source, lz.root_folder)
    # operational zone is expected to be empty:
    open(lz.path_to_start_state, "w").close()
    disable_write(lz.path_to_start_state)

    print_ok("+ example landing zone created", fg="green")
    return 0
