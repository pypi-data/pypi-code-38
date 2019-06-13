#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from enum import Enum
from logging import debug, basicConfig, DEBUG, info
from os import environ, system
from time import strftime
from typing import List, Tuple

from pyerge import utils, portage_tmpdir, tmplogfile, tmerge_logfile, dev_null

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


class World(Enum):
    PRETEND = ['-pvNDu', '@world']
    WORLD = ['-NDu', '@world']


class Tmerge:
    def __init__(self, world: World, verbose=False, deep_clean=False) -> None:
        self.world = world
        self.verbose = verbose
        self.deep_clean = deep_clean

    def emerge(self, arguments: List[str], verbose: bool, build=True) -> bytes:
        """
        Run emerge command.

        :param arguments:
        :param verbose:
        :param build:
        :return:
        """
        if verbose:
            info(f"running emerge with: {' '.join(arguments)}")
        if build:
            return_code = system(f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}")
            return bytes(return_code)
        else:
            output, _ = utils.run_cmd(f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}")
            return output

    def check(self, local_chk: bool, verbose: bool) -> None:
        """
        Check system updates.

        :param local_chk:
        :param verbose:
        """
        utils.delete_content(tmplogfile)
        utils.delete_content(tmerge_logfile)
        tmp = open(tmplogfile, 'w')
        log = open(tmerge_logfile, 'w')
        tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
        if not local_chk:
            if verbose:
                # info('Start syncing overlays...')
                # system(f'sudo layman -SN >> {tmplogfile} > {DEVNULL}')
                info('Start syncing portage...')
                debug(f'sudo eix-sync >> {tmplogfile} > {dev_null}')
            system(f'sudo eix-sync >> {tmplogfile} > {dev_null}')
            if verbose:
                info('Checking updates...')
        output = self.emerge('-pvNDu --color n @world'.split(), verbose, build=False)
        if verbose:
            info('Updates checked')
        log.write(output.decode(encoding='utf-8'))
        tmp.close()
        log.close()

        # system('sudo /usr/local/sbin/tmerge.py 1G -pvNDu --with-bdeps=y --color n @world >> %s' % logfile)
        if verbose:
            info('Creating log file...')
            debug(f'cat {tmerge_logfile} >> {tmplogfile}')
        system(f'cat {tmerge_logfile} >> {tmplogfile}')
        if verbose:
            debug(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}')
        system(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}')
        if verbose:
            info('Wrote to logs file')

    def is_running(self) -> bool:
        """
        Check if potrage command in currently running.

        :return: True if is running, False otherwise
        """
        if utils.run_cmd('pgrep -f /usr/bin/emerge'):
            return True
        return False

    def post_emerge(self, args: List[str], verbose: bool, return_code: bytes) -> None:
        """
        Run actions after emerge.

        :param args:
        :param verbose:
        :param return_code:
        """
        pretend, world = self.check_emerge_opts(args)
        if len(return_code) is 0 and not pretend and world:
            if verbose:
                info('Clearing emerge log')
            tmp = open(tmplogfile, 'w')
            log = open(tmerge_logfile, 'w')
            log.write('Total: 0 packages, Size of downloads: 0 KiB')
            tmp.close()
            log.close()

    def deep_clean(self, args: List[str], verbose: bool, return_code: bytes) -> None:
        """
        Run deep clean after emerge.

        :param args:
        :param verbose:
        :param return_code:
        """
        pretend, world = self.check_emerge_opts(args)
        if len(return_code) is 0 and not pretend and world:
            out = self.emerge(['-pc'], verbose, build=False)
            if verbose:
                info('Deep clean')
                debug(f'Details:{out.decode(encoding="utf-8")}')

    def check_emerge_opts(self, args: List[str]) -> Tuple[bool, bool]:
        """
        Check options in emerge command.

        :param args:
        :return:
        """
        pretend = True
        world = False
        if 'p' not in args[0] or 'f' in args[0]:
            pretend = False
        if 'world' in ' '.join(args):
            world = True
        return pretend, world

    @staticmethod
    def set_portage_tmpdir() -> None:
        """Set system variable."""
        if environ.get('PORTAGE_TMPDIR') is None:
            environ['PORTAGE_TMPDIR'] = portage_tmpdir
