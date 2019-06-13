# cli_util.py - default behaviors for CLI utilities
import argparse
import getpass
from smoacks.api_util import login

# Wraps arg-parse with default behavior for API login, accepts a dictionary
# of -- arg names and destination variable name strings
def get_opts(prog, desc, args):
    # Set up the argument parser for our command line options
    parser = argparse.ArgumentParser(prog=prog,
                                     description=desc)
    parser.add_argument('-u', dest='user')
    parser.add_argument('-p', dest='pwd')
    for arg in args:
        if len(arg) > 1:
            parser.add_argument('--{}'.format(arg), dest=args[arg])
        else:
            parser.add_argument('-{}'.format(arg), dest=args[arg])

    # Parse the actual arguments to this script
    opts = parser.parse_args()
    return opts

# Get an authenticated session based on user ID and password in opts
def get_session(opts):
    if 'user' not in opts or 'pwd' not in opts:
        return None
    return login(opts.user, opts.pwd)
