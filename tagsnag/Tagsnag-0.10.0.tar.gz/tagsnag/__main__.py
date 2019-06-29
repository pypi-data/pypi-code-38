##
#!/usr/bin/python
#
#  __main__.py
#  Tagsnag
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 31.10.2018.
#  Copyright (c) 2018 www.geeky.gent. All rights reserved.
#


import os
import sys
from argparse import ArgumentParser
from tagsnag.tagsnag import Tagsnag


def get_script_path():
    return os.path.dirname(__file__)


def main():
    try:
        cwd_path = os.getcwd()

        should_use_gui = (not len(sys.argv) > 1)

        tagsnag = Tagsnag(cwd_path, should_use_gui = should_use_gui)

        ##
        # Create argument parser
        ap = ArgumentParser()

        ##
        # Optionals grouped by category
        ap.add_argument('-d', '--destination', default=os.path.join(cwd_path, "Tagsnag"), help='Destination Path')
        ap.add_argument('-e', '--extension', help='Specify a file extension')
        ap.add_argument('-f', '--filename', help='String the filename contains')
        ap.add_argument('-dir', '--directory', help='Name of the folder you would like to extract')

        ap.add_argument('-t', '--tag', help='String the Tag you would like to checkout contains')

        ap.add_argument('-x', '--xml', help='Provide an xml config file')


        ##
        # Flags
        ap.add_argument('-l', '--log', default=False, action='store_true', help='Create Logfile')
        ap.add_argument('-p', '--prune', default=False, action='store_true', help='Prune on pull')
        ap.add_argument('-s', '--autostash', default=False, action='store_true', help='Enable autostash before checking out dirty directory')
        ap.add_argument('-u', '--update', default=False, action='store_true', help='Pull from origin/master into master prior to checkout')
        ap.add_argument('-v', '--verbose', default=False, action='store_true', help='Increase verbosity')

        ##
        # Validate / Parse provided arguments
        options = ap.parse_args()

        ##
        # Bind options
        destination = options.destination
        extension   = options.extension
        filename    = options.filename
        directory   = options.directory
        tag         = options.tag
        xml_path    = options.xml

        # Flags
        should_autostash      = options.autostash
        should_create_logfile = options.log
        should_prune          = options.prune
        should_update         = options.update
        verbose               = options.verbose

        ##
        #  Configuring tagsnag using the provided arguments
        tagsnag.set_verbose(verbose)
        tagsnag.set_should_autostash(should_autostash)
        tagsnag.set_should_prune(should_prune)
        tagsnag.set_create_logfile(should_create_logfile)

        if not should_use_gui:
            tagsnag.run_from_cli(should_update=should_update,
                                  xml_path=xml_path,
                                  tag=tag,
                                  directory=directory,
                                  destination=destination,
                                  filename=filename,
                                  extension=extension)


    except KeyboardInterrupt:
        tagsnag.log.info('Keyboard Interrupt detected: Exiting.')
        pass


if __name__ == "__main__":
    main()
