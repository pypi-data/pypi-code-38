#!/usr/bin/env python

""" cli to connect to Stormshield Network Security appliances"""

from __future__ import unicode_literals
import sys
import os
import re
import logging
import readline
import getpass
import atexit
import defusedxml.minidom
import argparse
import platform
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import TerminalFormatter
from colorlog import ColoredFormatter

from stormshield.sns.sslclient import SSLClient, ServerError

FORMATTER = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={},
    style='%'
)

EMPTY_RE = re.compile(r'^\s*$')

def make_completer():
    """ load completer for readline """
    vocabulary = []
    with open(SSLClient.get_completer(), "r") as completelist:
        for line in completelist:
            vocabulary.append(line.replace('.', ' ').strip('\n'))

    def custom_complete(text, state):
        results = [x for x in vocabulary if x.startswith(text)] + [None]
        return results[state]
    return custom_complete

def main():

    # parse command line

    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host",         help="Remote UTM",                 default=None)
    parser.add_argument("-i", "--ip",           help="Remote UTM ip",              default=None)
    parser.add_argument("-U", "--usercert",     help="CA bundle file",             default=None)
    parser.add_argument("-C", "--cabundle",     help="Remote UTM",                 default=None)
    parser.add_argument("-p", "--password",     help="Password",                   default=None)
    parser.add_argument("-P", "--port",         help="Remote port",                default=443, type=int)
    parser.add_argument("-u", "--user",         help="User name",                  default="admin")
    parser.add_argument("--sslverifypeer",      help="Strict SSL CA check",        default=True, action="store_true")
    parser.add_argument("--no-sslverifypeer",   help="Strict SSL CA check",        default=True, action="store_false", dest="sslverifypeer")
    parser.add_argument("--sslverifyhost",      help="Strict SSL host name check", default=True, action="store_true")
    parser.add_argument("--no-sslverifyhost",   help="Strict SSL host name check", default=True, action="store_false", dest="sslverifyhost")
    parser.add_argument("-c", "--credentials",  help="Privilege list",             default=None)
    parser.add_argument("-s", "--script",       help="Command script",             default=None)
    parser.add_argument("-o", "--outputformat", help="Output format (ini|xml)",    default="ini")

    exclusive  = parser.add_mutually_exclusive_group()
    exclusive.add_argument("-v", "--verbose", help="Increase logging output",     default=False, action="store_true")
    exclusive.add_argument("-q", "--quiet",   help="Decrease logging output",     default=False, action="store_true")

    group = parser.add_argument_group("logging", "Detailed control of logging output")
    group.add_argument("--loglvl",  help="Set explicit log level",      default=None,  choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    group.add_argument("--logfile", help='Output log messages to file', default=None)

    args = parser.parse_args()

    host = args.host
    ip = args.ip
    usercert = args.usercert
    cabundle = args.cabundle
    password = args.password
    port = 443
    user = 'admin'
    sslverifypeer = args.sslverifypeer
    sslverifyhost = args.sslverifyhost
    credentials = args.credentials
    script = args.script
    outputformat = 'ini'

    # logging

    level = logging.INFO
    if args.loglvl is not None:
        level = logging.getLevelName(args.loglvl)
    elif args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.WARNING
    # logger
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.setLevel(level)
    # handler
    if args.logfile is None:
        handler = logging.StreamHandler(sys.stdout)
    elif platform.system() != 'Windows':
        handler = logging.handlers.WatchedFileHandler(args.logfile)
    else:
        handler = logging.FileHandler(args.logfile)
    logger.addHandler(handler)

    for handler in logging.getLogger().handlers:
        if handler.__class__ == logging.StreamHandler:
            handler.setFormatter(FORMATTER)

    if script is not None:
        try:
            script = open(script, 'r')
        except Exception as exception:
            logging.error("Can't open script file - %s", str(exception))
            sys.exit(1)

    if outputformat not in ['ini', 'xml']:
        logging.error("Unknown output format")
        sys.exit(1)

    if host is None:
        logging.error("No host provided")
        sys.exit(1)

    if password is None and usercert is None:
        password = getpass.getpass()

    try:
        client = SSLClient(
            host=host, ip=ip, port=port, user=user, password=password,
            sslverifypeer=sslverifypeer, sslverifyhost=sslverifyhost,
            credentials=credentials,
            usercert=usercert, cabundle=cabundle, autoconnect=False)
    except Exception as exception:
        logging.error(str(exception))
        sys.exit(1)

    try:
        client.connect()
    except Exception as exception:
        search = re.search(r'doesn\'t match \'(.*)\'', str(exception))
        if search:
            logging.error(("Appliance name can't be verified, to force connection "
                           "use \"--host %s --ip %s\" or \"--no-sslverifyhost\" "
                           "options"), search.group(1), host)
        else:
            logging.error(str(exception))
        sys.exit(1)

    # disconnect gracefuly at exit
    atexit.register(client.disconnect)

    if script is not None:
        for cmd in script.readlines():
            cmd = cmd.strip('\r\n')
            print(cmd)
            if cmd.startswith('#'):
                continue
            if EMPTY_RE.match(cmd):
                continue
            try:
                response = client.send_command(cmd)
            except Exception as exception:
                logging.error(str(exception))
                sys.exit(1)
            if outputformat == 'xml':
                print(highlight(defusedxml.minidom.parseString(response.xml).toprettyxml(),
                                XmlLexer(), TerminalFormatter()))
            else:
                print(response.output)
        sys.exit(0)

    # Start cli

    # load history
    histfile = os.path.join(os.path.expanduser("~"), ".sslclient_history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    def save_history(histfile):
        try:
            readline.write_history_file(histfile)
        except:
            logging.warning("Can't write history")

    atexit.register(save_history, histfile)

    # load auto-complete
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims('')
    readline.set_completer(make_completer())

    while True:
        try:
            cmd = input("> ")
        except EOFError:
            break

        # skip comments
        if cmd.startswith('#'):
            continue

        try:
            response = client.send_command(cmd)
        except ServerError as exception:
            # do not log error on QUIT
            if "quit".startswith(cmd.lower()) \
               and str(exception) == "Server disconnected":
                sys.exit(0)
            logging.error(str(exception))
            sys.exit(1)
        except Exception as exception:
            logging.error(str(exception))
            sys.exit(1)

        if response.ret == client.SRV_RET_DOWNLOAD:
            filename = input("File to save: ")
            try:
                client.download(filename)
                logging.info("File downloaded")
            except Exception as exception:
                logging.error(str(exception))
        elif response.ret == client.SRV_RET_UPLOAD:
            filename = input("File to upload: ")
            try:
                client.upload(filename)
                logging.info("File uploaded")
            except Exception as exception:
                logging.error(str(exception))
        else:
            if outputformat == 'xml':
                print(highlight(defusedxml.minidom.parseString(response.xml).toprettyxml(),
                                XmlLexer(), TerminalFormatter()))
            else:
                print(response.output)

# use correct input function with python2
try:
    input = raw_input
except NameError:
    pass

if __name__ == "__main__":
    # execute only if run as a script
    main()
