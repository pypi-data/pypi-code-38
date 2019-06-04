import logging
import os
import shutil
import sys
import tarfile

from pytmpdir.Directory import Directory
from twisted.internet.defer import inlineCallbacks

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PeekSwInstallManagerABC import PEEK_PLATFORM_STAMP_FILE, \
    PeekSwInstallManagerABC
from peek_platform.util.PtyUtil import spawnPty, logSpawnException, spawnSubprocess
from vortex.DeferUtil import deferToThreadWrapWithLogger

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PeekSwUploadManager(object):
    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        newVersion, newPath = yield self.updateToTarFile(namedTempFile.name)

        # Tell the peek server to install and restart
        yield PeekPlatformConfig.peekSwInstallManager.installAndRestart(newVersion)

        return newVersion

    @deferToThreadWrapWithLogger(logger)
    def updateToTarFile(self, newSoftwareTar):
        """ Update To Tar File

        This method inspects the tar file and finally extracts it to the platform
        path.

        """

        directory = Directory()
        tarfile.open(newSoftwareTar).extractall(directory.path)
        directory.scan()

        self._testPackageUpdate(directory)

        platformVersionFile = [f for f in directory.files if
                               f.name == PEEK_PLATFORM_STAMP_FILE]
        if len(platformVersionFile) != 1:
            raise Exception("Uploaded archive does not contain a Peek Platform update"
                            ", Expected 1 %s file, got %s"
                            % (PEEK_PLATFORM_STAMP_FILE, len(platformVersionFile)))

        platformVersionFile = platformVersionFile[0]

        if '/' in platformVersionFile.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (PEEK_PLATFORM_STAMP_FILE, platformVersionFile.path))

        with platformVersionFile.open() as f:
            newVersion = f.read().strip()

        newPath = PeekSwInstallManagerABC.makeReleaseFileName(newVersion)

        # Do we really need to keep the old version if it's the same build?
        if os.path.isdir(newPath):
            shutil.rmtree(newPath)

        elif os.path.isfile(newPath):
            os.remove(newPath)

        shutil.copy(newSoftwareTar, newPath)

        return newVersion, newPath

    def _testPackageUpdate(self, directory: Directory) -> None:
        """ Test Package Update

        :param directory: The directory where the packages are extracted

        Since we ARE running on the server, we will test install these packages here
         first, this is done by creating a virtualenv.

        There isn't a lot of testing for the release at this stage.
        Currently we just use pip to try and install the packages off line, if it's happy
         we're happy.

        """

        # Create the test virtualenv
        virtualEnvDir = Directory()

        virtExec = os.path.join(os.path.dirname(sys.executable), "virtualenv")
        virtArgsList= [virtExec,
                    # Give the virtual environment access to the global
                    '--system-site-packages',
                    virtualEnvDir.path]
        virtArgs = ' '.join(virtArgsList)

        try:
            spawnSubprocess(virtArgs)
            logger.debug("Vritual env created.")

        except Exception as e:
            logSpawnException(e)
            raise Exception("Failed to create virtualenv for platform test")

        # We could use import pip, pip.main(..), except:
        # We want to capture, the output, and:
        # we can't tell it to use the virtualenv

        pipExec = os.path.join(virtualEnvDir.path, 'bin', 'pip')

        # Install all the packages from the directory
        pipArgs = [pipExec] + PeekSwInstallManagerABC.makePipArgs(directory)
        pipArgs = ' '.join(pipArgs)

        try:
            spawnPty(pipArgs)

        except Exception as e:
            logSpawnException(e)

            # Update the detail of the exception and raise it
            raise Exception("Test install of updated package failed.")

        # Continue normally if it all succeeded
        logger.debug("Peek update successfully tested.")
