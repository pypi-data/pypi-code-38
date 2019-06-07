#!/usr/bin/python
"""
A Python driver for Honeywell's SPM Flex gas detector, using HTTP SOAP.

Distributed under the GNU General Public License v2
Copyright (C) 2019 NuMat Technologies
"""
from spmflex.driver import GasDetector


def command_line():
    """Command-line tool for SPM Flex gas detector communication."""
    import argparse
    import asyncio
    import json

    parser = argparse.ArgumentParser(description="Read a Honeywell SPM Flex "
                                     "gas detector state.")
    parser.add_argument('address', help="The IP address of the gas detector.")
    parser.add_argument('-r', '--raw', action='store_true', help="Return all "
                        "available output as an uncleaned dictionary.")
    args = parser.parse_args()

    async def get():
        async with GasDetector(args.address) as detector:
            print(json.dumps(await detector.get(raw=args.raw), indent=4, sort_keys=True))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get())
    loop.close()


if __name__ == '__main__':
    command_line()
