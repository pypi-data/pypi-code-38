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


# This is the main entry for the command 'htv' of the application
def entry():
    # If 'htv' has arguments, depending on the argument a different function will be executed
    if len(sys.argv) > 1:
        # It saves the arguments in a list
        arguments = sys.argv[1:]
        for arg in arguments:
            # It the arg is --install or -i the install func will be launched (it creates the main dir htv and subdirs)
            if "--install" == arg or "-i" == arg:
                install()
            # It the arg is --shadow or -s the shadow func will be launched (it asks for Openrc pwd and save them)
            elif "--shadow" == arg or "-s" == arg:
                shadow()
            # If the arg is an openrc.sh file it will be used for the OS authentication and the app goes no-inter. mode
            elif "openrc" in arg:
                pwd, path_to_file = no_interactive(arg)
                clients = config(pwd, path_to_file)
                validate_template(clients)
            else:
                printout(">> Wrong option\n", RED)
    # If there are no args the main command 'htv' will be executed
    else:
        # It first checks if the main directory exists, if yes, the app goes in interactive mode
        if os.path.exists("{}/htv".format(home)):
            pwd, path_to_file = interactive()
            clients = config(pwd, path_to_file)
            validate_template(clients)
        # If the main app dir does not exist the user has to execute 'htv -i' first
        else:
            printout(">> Execute 'htv -i' first\n", RED)
