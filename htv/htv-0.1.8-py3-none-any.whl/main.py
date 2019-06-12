# System imports
import sys
import os
from htvalidator.install import install
from htvalidator.shadow import shadow
from htvalidator.validate import validate_template
from htvalidator.config.auth_config import config
from htvalidator.os_utility.miscellanea import interactive, no_interactive, printout

home = os.environ['HOME']
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


# TODO comment everything you disgraziata
# TODO accept multiple args (openrc and passwd)

def entry():
    if len(sys.argv) > 1:
        # It saves the arguments in a list
        arguments = sys.argv[1:]
        for arg in arguments:
            if "--install" in arg or "-i" in arg:
                install()
            elif "--shadow" in arg or "-s" in arg:
                shadow()
            elif "openrc" in arg:
                pwd, path_to_file = no_interactive(arg)
                clients = config(pwd, path_to_file)
                validate_template(clients)
            else:
                printout(">> Wrong option\n", RED)
    else:
        if os.path.exists("{}/htv".format(home)):
            pwd, path_to_file = interactive()
            clients = config(pwd, path_to_file)
            validate_template(clients)
        else:
            printout(">> Execute 'htv -i' first\n", RED)
