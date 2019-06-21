#!/usr/bin/env python3
"""
Remove an excess of files.

Implement a files retention policy such that more copies of recent files are
kept; files are deleted as they get older.

For instance, keep 1 file every day for 1 week, 1 file every week for 1 month,
1 file every month for 1 year, 1 file every year forever.

By default, print on stdout the names of the files to delete.
"""

import re
import sys
import logging
import datetime as dt
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    RawDescriptionHelpFormatter,
)

logger = logging.getLogger('weeder')

DEFAULT_NAME_PATTERN = r'(\d{4})-(\d{2})-(\d{2})'
DEFAULT_POLICY = ((14, 7), (84, 28), (364, 364))


class Weeder:
    def __init__(self, files, refdate, policy=None, format=None):
        self.files = files
        self.refdate = refdate
        self.policy = policy or DEFAULT_POLICY
        self.format = self.parse_pattern(format or DEFAULT_NAME_PATTERN)

        self.dates_map = self.get_dates_map()

    class Error(Exception):
        """Error in the weeder processing."""

    def get_files_to_delete(self):
        keepers = set(self.get_files_to_keep())
        return [f for f in self.files if f not in keepers]

    def get_files_to_keep(self):
        dates = set(self.get_dates_to_keep(self.dates_map.keys()))
        outfiles = {self.dates_map[d] for d in dates}
        return [f for f in self.files if f in outfiles]

    def get_dates_to_keep(self, dates):
        dates = sorted(dates, reverse=True)
        policy = sorted(self.policy, reverse=True)

        for threshold, distance in policy:
            threshold = self.refdate - dt.timedelta(days=threshold)
            logger.debug("threshold: %s, distance: %d", threshold, distance)
            band = []
            while dates and dates[-1] <= threshold:
                band.append(dates.pop())

            if not band:
                continue

            logger.debug("dates between: %s and %s", band[0], band[-1])
            last = None
            for d in band:
                if last is None or (d - last).days >= distance:
                    logger.debug("will keep: %s", d)
                    yield d
                    last = d
                else:
                    logger.debug("will discard: %s", d)

        dates.reverse()
        for d in dates:
            yield d

    def parse_pattern(self, format):
        try:
            return re.compile(format)
        except Exception as e:
            raise self.Error("error parsing format '%s': %s" % (format, e))

    def get_dates_map(self):
        rv = {}
        for fn in self.files:
            d = self.get_date_from_file(fn)
            if d is None:
                continue
            if d in rv:
                raise self.Error(
                    "files '%s' and '%s' have the same date" % (rv[d], fn)
                )

            rv[d] = fn

        return rv

    def get_date_from_file(self, filename):
        m = self.format.search(filename)
        if m is None:
            logger.warning("file doesn't match format: %s", filename)
            return

        g = m.groups()
        if len(g) != 3:
            raise self.Error(
                "the format didn't find 3 values in: %s", filename
            )

        try:
            d = dt.date(*(int(x) for x in g))
        except Exception:
            raise self.Error(
                "the file doesn't represent a valid date: %s", filename
            )

        logger.debug("got date %s for file: %s", d, filename)
        return d


def run_cmdline(args=None, outfile=None):
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
    )
    opt = parse_cmdline(args)
    logger.setLevel(opt.loglevel)

    w = Weeder(
        files=opt.files,
        refdate=opt.refdate,
        policy=opt.policy,
        format=opt.format,
    )
    if opt.print_keepers:
        for f in w.get_files_to_keep():
            print(f, file=outfile or sys.stdout)
    else:
        for f in w.get_files_to_delete():
            print(f, file=outfile or sys.stdout)


def parse_cmdline(args=None):
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )

    def parse_date(s):
        try:
            return dt.datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            raise ArgumentTypeError("not a valid date: %s" % s)

    def parse_policy(s):
        try:
            a, r = s.split(':')
            return int(a), int(r)
        except Exception:
            raise ArgumentTypeError("not a valid policy: %s" % s)

    parser.add_argument(
        'files', metavar='FILE', nargs='*', help="the files to weed"
    )

    parser.add_argument(
        '-p',
        '--policy',
        metavar="AGE:DIST",
        nargs='+',
        type=parse_policy,
        help="""
            state that, of every file older than AGE days, we want to keep at
            least one every DIST days [default: %s]
            """
        % " ".join("%s:%s" % p for p in DEFAULT_POLICY),
    )

    parser.add_argument(
        '-f',
        '--format',
        metavar="REGEX",
        default=DEFAULT_NAME_PATTERN,
        help="the pattern to extract a date from a file name"
        " [default: %(default)s]",
    )

    parser.add_argument(
        '-r',
        '--refdate',
        metavar="YYYY-MM-DD",
        help="reference date to establish retention [default: today]",
        type=parse_date,
        default=dt.date.today(),
    )

    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        '--print-keepers',
        dest='print_keepers',
        action='store_true',
        help="print the files to keep",
    )
    g.add_argument(
        '--print-goners',
        dest='print_keepers',
        action='store_false',
        default=False,
        help="print the files to delete [default]",
    )

    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        '-q',
        '--quiet',
        help="talk less",
        dest='loglevel',
        action='store_const',
        const=logging.WARN,
        default=logging.INFO,
    )
    g.add_argument(
        '-v',
        '--verbose',
        help="talk more",
        dest='loglevel',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
    )

    opt = parser.parse_args(args)
    return opt


def main():
    try:
        sys.exit(run_cmdline())

    except Weeder.Error as e:
        logger.error("%s", e)
        sys.exit(1)

    except Exception:
        logger.exception("unexpected error")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("user interrupt")
        sys.exit(1)


if __name__ == '__main__':
    main()
