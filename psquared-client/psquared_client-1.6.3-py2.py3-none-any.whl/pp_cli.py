#
# Module: pp-cli
#
# Description: PSquared command line interface
#

from __future__ import print_function

MISSING_ARGUMENT=1
MISSING_ARGUMENT_MESSAGE='Missing argument'
MISSING_OPTION=2
MISSING_OPTION_MESSAGE='Missing option'
MULIPLE_TRANSITIONS=3
MULIPLE_TRANSITIONS_MESSAGE='Multiple transitions'

import sys

def eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)


def verify_args(config, version):
    if None == config:
        eprint(MISSING_OPTION_MESSAGE + ': Configuration must be supplied')
        sys.exit(MISSING_OPTION)
    if None == version:
        eprint(MISSING_OPTION_MESSAGE + ': Version must be supplied')
        sys.exit(MISSING_OPTION)


def setTransition(current, requested):
    if None != current and current != requested:
        eprint(MULTIPLE_TRANSITIONS_MESSAGE + ': Only one type of transition is possible per invocation')
        sys.exit(MULIPLE_TRANSITIONS)
    return requested


import os
from psquared_client import Display, PSquared, FatalError

def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Command Line interface to a PSquared server.')
    parser.add_argument('-?',
                        help = 'Prints out this help',
                        action = 'help')
    parser.add_argument('--abandon',
                        dest = 'ABANDON',
                        help = 'abandons the processing of items with the specified configuration if they have failed,'
                        + ' i.e. they will be ignored in responses to a request for info or unprocessed items. (This is a shortcut for "-t abandon.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--cacert',
                        dest = 'CA_CERTIFICATE',
                        help = 'path to the file containing one or more CA x509 certificates, if different from the default,'
                        + ' ${HOME}/.psquared/client/cert/cacert.pem',
                        default = None)
    parser.add_argument('--cancel',
                        dest = 'CANCEL',
                        help = 'cancels  processing of the items with the specified configuration if they have not completed,'
                        + ' i.e. they can be re-submitted later. (This is a shortcut for "-t cancel.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--cert',
                        dest = 'CERTIFICATE',
                        help = 'path to the client\'s x509 certificate, if different from the default, ${HOME}/.psquared/client/cert/psquare_client.pem',
                        default = None)
    parser.add_argument('--create',
                        dest = 'CREATION_FILE',
                        help = 'reads the specified file and creates the appropriate configurations and versions. '
                        + 'Note: the .py extension does not have to be specified, but is required in the files actual name.',
                        default = None)
    parser.add_argument('-d',
                        '--debug',
                        dest='DEBUG',
                        help='print out RESTful documents.',
                        action='store_true',
                        default=False)
    parser.add_argument('-f',
                        '--file',
                        dest = 'FILE',
                        help = 'the name of a file containing a list of items which will be added to any specified on the command line',
                        default = None)
    parser.add_argument('-H',
                        '--history',
                        dest = 'HISTORY',
                        help = 'the processing history of the items with the specified configuration. (Overrides "-i".)',
                        action = 'store_true',
                        default = False)
    parser.add_argument('-i',
                        '--info',
                        dest = 'INFO',
                        help = 'provide information on either the application when no configuration is specified,'
                        + ' the configuration when no version is specified,'
                        + ' or the current processing state of the items with the specified configuration/version.',
                        action = 'store_true',
                        default = True)
    parser.add_argument('--key',
                        dest = 'KEY',
                        help = 'path to the client\'s private x509 key, if different from the default, ${HOME}/.psquared/client/private/psquare_client.key',
                        default = None)
    parser.add_argument('-m',
                        '--message',
                        dest = 'MESSAGE',
                        help = 'adds the specified text as a option message to a requested change in the items/configuration pairings',
                        default = None)
    parser.add_argument('-q',
                        '--quiet',
                        dest = 'QUIET',
                        help = 'stop the results of any transition execution from being displayed. Explicit request for info will still produce output',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--recover',
                        dest = 'RECOVER',
                        help = 'returns an abandoned processing of items with the specified configuration so that is can be re-submitted later.'
                        + ' (This is a shortcut for "-t recover.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--reset',
                        dest = 'RESET',
                        help = 'resets the processing of items with the specified configuration if they have completed,'
                        + ' i.e. they it can be re-submitted later. (This is a shortcut for "-t reset.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--resolved',
                        dest = 'RESOLVED',
                        help = 'resets the processing items with the specified configuration if they have failed, i.e. they it can be re-submitted later.'
                        + ' (This is a shortcut for "-t resolved.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('--scheduler',
                        dest = 'SCHEDULER',
                        help = 'uses the named scheduler to submit items for processing with the specified configuration rather than the default one.',
                        default = None)
    parser.add_argument('-s',
                        '--submit',
                        dest = 'SUBMIT',
                        help = 'submits the items for processing with the specified configuration pair,'
                        + ' if they are ready. (This is a shortcut for "-t submit.")',
                        action = 'store_true',
                        default = False)
    parser.add_argument('-t',
                        '--transition',
                        dest = 'TRANSITION',
                        help = 'the transition for the items with the specified configuration/version that should be executed.',
                        default = None)
    parser.add_argument('--template',
                        dest = 'TEMPLATE_FILE',
                        help = 'writes out a creation template to the specified file.',
                        default = None)
    parser.add_argument('-u',
                        '--unprocessed',
                        dest = 'UNPROCESSED',
                        help = 'lists the set of items that have been submitted but not successfully processed by the specified configuration/version',
                        action = 'store_true',
                        default = False)
    parser.add_argument('-V',
                        dest = 'VERSION',
                        help = 'the version of the specified configuration to use if not the default one',
                        default = None)
    parser.add_argument('--veto',
                        dest = 'VETO',
                        help = 'the name of the veto, is any, to apply to the submission. ("family" is the only supported one at the moment)',
                        default = None)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    args = options.args

    if 0 == len(args):
        config = None
        items = []
    else:
        config = args[0]
        if 1 == len(args):
            items = []
        else:
            items = args[1:]

    if None != options.FILE:
        f = open(options.FILE, 'r')
        lines = f.readlines()
        for line in lines:
            if 0 != len(line) and '\n' == line[-1:]:
                item = line[:-1].strip()
            else:
                item = line[0:-1].strip()
            if '' != item and not item.startswith('#'):
                items.append(item)

    url = os.getenv('PP_APPLICATION', 'http://localhost:8080/psquared/local/report/')
    psquared = PSquared(url, xml=options.DEBUG, cert = options.CERTIFICATE, key = options.KEY, cacert = options.CA_CERTIFICATE )
    if options.DEBUG:
        psquared.debug_separator()

    transition = options.TRANSITION
    if options.SUBMIT:
        transition = setTransition(transition, 'submit')
    if options.RESOLVED:
        transition = setTransition(transition, 'resolved')
    if options.CANCEL:
        transition = setTransition(transition, 'cancel')
    if options.RESET:
        transition = setTransition(transition, 'reset')
    if options.ABANDON:
        transition = setTransition(transition, 'abandon')
    if options.RECOVER:
        transition = setTransition(transition, 'recover')

    try:
        run_default = True
        if options.INFO and None != config:
            if None == options.VERSION:
                if 0 != len(items):
                    eprint(MISSING_OPTION_MESSAGE + ': Version must be supplied when one of more items are specified')
                    sys.exit(MISSING_OPTION)
                configuration, application = psquared.get_configuration(config)
                Display.versions(configuration)
            else:
                report, version = psquared.get_report(config, options.VERSION, 'current', items)
                Display.info(config, version, report, items)
            run_default = False

        if options.TEMPLATE_FILE:
            psquared.write_template(options.TEMPLATE_FILE)
            run_default = False

        if options.CREATION_FILE:
            configCount, versCount = psquared.create_from_file(options.CREATION_FILE)
            if 0 != configCount:
                if 1 == configCount:
                    plural = ''
                else:
                    plural = 's'
                print('Added ' + str(configCount) + " configuration" + plural)
            if 0 != versCount:
                if 1 == versCount:
                    plural = ''
                else:
                    plural = 's'
                print('Added ' + str(versCount) + " version" + plural)
            run_default = False

        if options.HISTORY:
            verify_args(config, options.VERSION)
            report, version = psquared.get_report(config, options.VERSION, 'histories', items)
            Display.histories(config, version, report, items)
            run_default = False

        if options.UNPROCESSED:
            verify_args(config, options.VERSION)
            report, version = psquared.get_report(config, options.VERSION, 'unprocessed')
            Display.info(config, version, report)
            run_default = False

        if None != transition:
            if 'submit' == transition:
               report, version = psquared.execute_submissions(config, options.VERSION, items,
                                                              options.MESSAGE, options.QUIET, options.SCHEDULER, options.VETO)
               if None != report:
                  Display.info(config, version, report, items)
            else:
               report, version = psquared.get_report(config, options.VERSION, 'current', items)
               result = psquared.execute_transitions(config, version, report, items, transition, options.MESSAGE, options.QUIET)
               Display.info(config, version, result, items)
            run_default = False

        if run_default or (options.INFO and None == config):
            # Default with nothing specified is to list all known configurations.
            application = psquared.get_application()
            Display.configurations(application)

    except FatalError as e:
        eprint(e.message)
        sys.exit(e.code)


if __name__ == '__main__':
    main()
