import logging
import os

import pathspec

import qsa.const
from qsa.lib.pathfinder import Pathfinder


class AssemblerConfig:
    logger = logging.getLogger('qsa')

    def __init__(self, workdir=None):
        self.workdir = workdir or os.getcwd()
        self.pathfinder = Pathfinder(self.workdir)
        self.ignored = self._readignored()

    def getcwd(self):
        """Return the current working directory of the Quantum Service
        Assembler (QSA).
        """
        return self.workdir

    def isignored(self, path):
        """Return a boolean indicating if the `path` is ignored by the
        the project.
        """
        return self.ignored.match_file(path)

    def ignore(self, pattern):
        """Excludes the given pattern, filename or directory name from
        all QSA operations.
        """
        fp = self.pathfinder.abspath(qsa.const.QUANTUMIGNORE)
        mode = 'w' if not self.pathfinder.exists(fp)\
            else 'a'
        with open(fp, mode) as f:
            f.write(f'{pattern}\n')

    def _readignored(self):
        patterns = pathspec.PathSpec([])
        if self.pathfinder.exists(qsa.const.QUANTUMIGNORE):
            with open(self.pathfinder.abspath(qsa.const.QUANTUMIGNORE)) as f:
                patterns = pathspec.PathSpec.from_lines('gitwildmatch',
                    f)
            self.logger.debug("Loaded ignore patterns from %s",
                qsa.const.QUANTUMIGNORE)
        else:
            self.logger.debug("%s not found, no files are ignored.",
                qsa.const.QUANTUMIGNORE)

        return patterns
