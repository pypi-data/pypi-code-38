'''
Write a set of configuration options from the command line
'''

from . import log
import argparse

if __name__ == '__main__':
    def _cli():
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', nargs=2, action='append')
        parser.add_argument('-t', dest='title')
        parser.add_argument('-l', '--logfile', dest='logfile',
                help='(REQUIRED) name of file to write configuration contents to',
                default=None)
        options = parser.parse_args()
        if not options.logfile:
            parser.print_help()
            exit()
        return options

    options = _cli()
    log.start(logfile=options.logfile)
    log.writeConfig(
        settings=options.o,
        title=options.title
    )
    log.stop()
