"""
Usage:
  vshock <path> [options]

Where:
  <path> is the location to make input stream of the virtual controller.

Options:
  -h --help       Show this help.
  --port <number> Specify the port number to listen.
  -b --browser    Open the browser automatically.
"""

import sys
from docopt import docopt
from .io import create_fifo
from .server import serve


def main():
    """
    Parse command line arguments and start the application.
    """
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    args = docopt(__doc__)

    path = args['<path>']
    port = args['--port']
    if not port:
        port = '8080'
    browser = args['--browser']

    create_fifo(args['<path>'])
    serve(port, path, browser)
