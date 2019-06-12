# ©2018 - Tim van Leuverden <TvanLeuverden@Gmail.com>
import argparse
import logging
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from .assistant import Assistant
from .crc32 import Crc32
from .vars import VERSION


def main():
    parser = argparse.ArgumentParser(description="Ruri")
    parser.add_argument("-r", "--recursive", help="work recursively", action="store_true")
    parser.add_argument("-t", "--threads", help="override the amount of threads", type=int, default=1)
    parser.add_argument("-v", "--verbose", help="output level", action="store_true")
    parser.add_argument("-q", "--quiet", help="Do not print progressbars.", action="store_true")
    parser.add_argument("--version", help="Print the version number, and exit.", action="version",
                        version="%(prog)s version " + VERSION)
    parser.add_argument("file", nargs='+', help="The file(s) you need CRC'ed")
    try:
        args = parser.parse_args()
    except Exception as ex:
        Assistant(False).logger.warn(ex)
        Assistant(False).print_end(1)

    assistant = Assistant(args.quiet)
    crc32 = Crc32(assistant)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s]\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    threads = args.threads
    assistant.logger.debug("Threads set at %s" % str(args.threads))

    try:
        if args.recursive:
            recursive(assistant, crc32, threads, args)
        else:
            normal(assistant, crc32, threads, args)
    except KeyboardInterrupt:
        if not assistant.quiet_mode:
            assistant.print_end(2)
    except Exception as ex:
        if not assistant.quiet_mode:
            assistant.logger.warning(ex)
            assistant.print_end(3)


def normal(assistant, crc32, threads, args):
    assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
    pool = ThreadPool(threads)
    pool.map(crc32.crc32, args.file)
    pool.close()
    pool.join()
    if not assistant.quiet_mode:
        return assistant.print_end(0)
    else:
        return sys.exit(0)


def recursive(assistant, crc32, threads, args):
    if not assistant.quiet_mode:
        assistant.logger.warning(
            "%s\t%s" % (
                assistant.text_purple("WARNING"),
                assistant.text_red("Experimental feature")
            )
        )
    assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
    file_set = set()
    pool = ThreadPool(threads)
    for root_dir in args.file:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                rel_dir = os.path.relpath(root, ".")
                rel_file = os.path.join(rel_dir, file)
                file_set.add(rel_file)
        pool.map(crc32.crc32, file_set)
        pool.close()
    pool.join()
    if not assistant.quiet_mode:
        assistant.print_end(0)
    else:
        sys.exit(0)
