#!/usr/bin/env python

# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-14 12:32:23 +0300 (Tue, 14 May 2019) $
# $Revision: 592 $


"""
This module implements a command line parser for the "Hardware Test Platform"
from Hilscher.

*Set value using telnet:*

```
htptools -p telnet set --host 192.168.199.31 --pin 14 --val 1
```

*Get value using socket:*
```
python -m htpio -p socket get --host 192.168.199.31 --pin 14 or
htpio -p socket get --host 192.168.199.31 --pin 14
```

*Lock/Unlock pin:*
```
htptools -p telnet lock --host 192.168.199.31 --pin 14
htptools -p socket unlock --host 192.168.199.31 --pin 14
```

"""

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import argparse

# Local imports
from htpio import telnetio
from htpio import socketio
from htpio import bridge

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARSER FUNCTIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Function get
def func_get(args):
    if args.protocol == 'telnet':
        device = telnetio.RaspberryPi(args.host)

    elif args.protocol == 'socket':
        device = socketio.RaspberryPi(args.host)

    else:
        device = telnetio.RaspberryPi(args.host)

    gpio = bridge.RemoteAccess(device)
    print(gpio.get(args.pin))


# Function set
def func_set(args):
    if args.protocol == 'telnet':
        device = telnetio.RaspberryPi(args.host)

    elif args.protocol == 'socket':
        device = socketio.RaspberryPi(args.host)

    else:
        device = telnetio.RaspberryPi(args.host)

    gpio = bridge.RemoteAccess(device)
    gpio.configure(args.pin, gpio.OUTPUT)
    gpio.set(args.pin, args.val)


# Function lock
def func_lock(args):
    if args.protocol == 'telnet':
        device = telnetio.RaspberryPi(args.host)

    elif args.protocol == 'socket':
        device = socketio.RaspberryPi(args.host)

    else:
        device = telnetio.RaspberryPi(args.host)

    gpio = bridge.RemoteAccess(device)
    gpio.lock(args.pin)


# Function unlock
def func_unlock(args):
    if args.protocol == 'telnet':
        device = telnetio.RaspberryPi(args.host)

    elif args.protocol == 'socket':
        device = socketio.RaspberryPi(args.host)

    else:
        device = telnetio.RaspberryPi(args.host)

    gpio = bridge.RemoteAccess(device)
    gpio.reset(args.pin)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARSER DEFINITION
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def parser():
    argparser = argparse.ArgumentParser(
        description="HTP Library CLI",
        usage="htptools [OPTIONS] COMMAND [ARGS]",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="For help type htptools [COMMAND] -h | --help"
    )

    group = argparser.add_argument_group(title="OPTIONS")

    # Protocol option
    group.add_argument(
        '-p',
        dest='protocol',
        default='telnet',
        help='Protocol to use (telnet, socket)'
    )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Define subcommands
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    subparsers = argparser.add_subparsers(
        title="COMMAND",
    )

    # Set
    setcmd = subparsers.add_parser('set', help='set pin value')

    setcmd.add_argument('--host',
                        default='192.168.199.31',
                        help="server address")

    setcmd.add_argument('--port',
                        default=23,
                        help="server port")

    setcmd.add_argument('--pin',
                        type=int,
                        help='pin number')

    setcmd.add_argument('--val',
                        type=int,
                        help='signal value')

    setcmd.set_defaults(func=func_set)

    # Get
    getcmd = subparsers.add_parser('get', help='get pin value')

    getcmd.add_argument('--host',
                        default='192.168.199.31',
                        help="server address")

    getcmd.add_argument('--port',
                        default=23,
                        help="server port")

    getcmd.add_argument('--pin',
                        type=int,
                        help='pin number')

    getcmd.set_defaults(func=func_get)

    # Lock
    lockcmd = subparsers.add_parser('lock', help='locks pin')

    lockcmd.add_argument('--host',
                         default='192.168.199.31',
                         help="server address")

    lockcmd.add_argument('--port',
                         default=23,
                         help="server port")

    lockcmd.add_argument('--pin',
                         type=int,
                         help='pin number')

    lockcmd.set_defaults(func=func_lock)

    # Unlock
    unlockcmd = subparsers.add_parser('unlock', help='unlocks pin')

    unlockcmd.add_argument('--host',
                           default='192.168.199.31',
                           help="server address")

    unlockcmd.add_argument('--port',
                           default=23,
                           help="server port")

    unlockcmd.add_argument('--pin',
                           type=int,
                           help='pin number')

    unlockcmd.set_defaults(func=func_unlock)

    # cmd_01 = "-p socket set --host 192.168.199.31 --port 23 --pin 14 --val 1"
    # args = argparser.parse_args(cmd_01.split())

    # cmd_02 = "-p socket set --host 192.168.199.31 --port 23 --pin 14 --val 0"
    # args = argparser.parse_args(cmd_02.split())

    # cmd_03 = "-p socket lock --host 192.168.199.31 --port 23 --pin 14"
    # args = argparser.parse_args(cmd_03.split())

    # cmd_04 = "-p socket unlock --host 192.168.199.31 --port 23 --pin 14"
    # args = argparser.parse_args(cmd_04.split())

    args = argparser.parse_args()

    try:
        args.func(args)

    except AttributeError:
        argparser.print_help()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN PROGRAM
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

main = parser

if __name__ == '__main__':
    main()
