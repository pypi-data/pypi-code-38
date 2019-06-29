import logging

import os
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class BuilderABC(metaclass=ABCMeta):

    def _writeFileIfRequired(self, dir, fileName, contents):
        fullFilePath = os.path.join(dir, fileName)

        # Apply any changes to these files using the transform code
        contents = self._syncFileHook(fileName, contents.encode()).decode()

        # Since writing the file again changes the date/time,
        # this messes with the self._recompileRequiredCheck
        if os.path.isfile(fullFilePath):
            with open(fullFilePath, 'r') as f:
                if contents == f.read():
                    logger.debug("%s is up to date", fileName)
                    return

        logger.debug("Writing new %s", fileName)

        with open(fullFilePath, 'w') as f:
            f.write(contents)


    @abstractmethod
    def _syncFileHook(self, fileName: str, contents: bytes) -> bytes:
        """ Sync File Hook

        see FrontendFileSync._syncFileHook

        """
        pass

    def _recompileRequiredCheck(self, feBuildDir: str, hashFileName: str) -> bool:
        """ Recompile Check

        This command lists the details of the source dir to see if a recompile is needed

        The find command outputs the following

        543101    0 -rw-r--r--   1 peek     sudo            0 Nov 29 17:27 ./src/app/environment/environment.component.css
        543403    4 drwxr-xr-x   2 peek     sudo         4096 Dec  2 17:37 ./src/app/environment/env-worker
        543446    4 -rw-r--r--   1 peek     sudo         1531 Dec  2 17:37 ./src/app/environment/env-worker/env-worker.component.html

        """

        excludeFilesEndWith = (".git", ".idea", '.lastHash')
        excludeFilesStartWith = ()

        def dirCheck(path):
            s = os.path.sep
            excludePathContains = ('__pycache__', 'node_modules', 'platforms', 'dist')

            # Always include the node_modules/@peek module dir
            if path.endswith(s + "@peek") or (s + "@peek" + s) in path:
                return True

            for exPath in excludePathContains:
                # EG "C:\thing\node_modules"
                if path.endswith(s + exPath):
                    return False

                # EG "C:\thing\node_modules\thing"
                if (s + exPath + s) in path:
                    return False

            return True

        fileList = []

        for (path, directories, filenames) in os.walk(feBuildDir):
            if not dirCheck(path):
                continue

            for filename in filenames:
                if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                    continue

                if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                    continue

                fullPath = os.path.join(path, filename)
                relPath = fullPath[len(feBuildDir) + 1:]
                stat = os.stat(fullPath)
                fileList.append('%s %s %s' % (relPath, stat.st_size, stat.st_mtime))

        newHash = '\n'.join(fileList)
        fileHash = ""

        if os.path.isfile(hashFileName):
            with open(hashFileName, 'r') as f:
                fileHash = f.read()

        fileHashLines = set(fileHash.splitlines())
        newHashLines = set(newHash.splitlines())
        changes = False

        for line in fileHashLines - newHashLines:
            changes = True
            logger.debug("Removed %s" % line)

        for line in newHashLines - fileHashLines:
            changes = True
            logger.debug("Added %s" % line)

        if changes:
            with open(hashFileName, 'w') as f:
                f.write(newHash)

        return changes
