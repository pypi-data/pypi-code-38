# System imports
import sys
from htvalidator.install import install
from htvalidator.shadow import shadow
from htvalidator.validate import validate_template
from htvalidator.os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def entry():
    if len(sys.argv) > 1:
        # It saves the arguments in a list
        arguments = sys.argv[1:]
        for arg in arguments:
            if "--install" in arg or "-i" in arg:
                install()
            elif "--shadow" in arg or "-s" in arg:
                shadow()
            else:
                printout(">> Wrong option\n", RED)
    else:
        validate_template()
