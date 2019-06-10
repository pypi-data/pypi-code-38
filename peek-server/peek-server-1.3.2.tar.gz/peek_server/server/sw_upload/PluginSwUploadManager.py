import logging
import os
import shutil
import sys
import tarfile
from tempfile import NamedTemporaryFile

import jsoncfg
from jsoncfg.value_mappers import require_string
from pytmpdir.Directory import Directory, File
from twisted.internet.defer import inlineCallbacks, returnValue

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PluginSwInstallManagerABC import PLUGIN_PACKAGE_JSON, \
    PluginSwInstallManagerABC
from peek_platform.util.PtyUtil import spawnSubprocess, logSpawnException, spawnPty
from peek_server.server.sw_version.PeekSwVersionDataHandler import \
    peekSwVersionDataHandler
from peek_server.storage.PeekPluginInfo import PeekPluginInfo

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PluginSwUploadManager(object):
    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        # We need the file to end in .tar.gz
        # PIP doesn't like it otherwise
        namedTempTarGzFile = NamedTemporaryFile(
            dir=PeekPlatformConfig.config.tmpPath, suffix=".tar.gz")
        shutil.copy(namedTempFile.name, namedTempTarGzFile.name)
        del namedTempFile

        pluginName, pluginVersion, fullNewTarPath = yield self.updateToTarFile(
            namedTempTarGzFile)

        # Cascade this update to all the other Peek environment components
        yield PeekPlatformConfig.pluginSwInstallManager.installAndReload(
            pluginName, pluginVersion, fullNewTarPath)

        # Cascade this update to all the other Peek environment components
        yield peekSwVersionDataHandler.notifyOfVersion(pluginName, pluginVersion)

        returnValue("%s, %s" % (pluginName, pluginVersion))

    def updateToTarFile(self, namedTempTarGzFile):

        dirName = tarfile.open(namedTempTarGzFile.name).getnames()[0]

        directory = Directory()
        tarfile.open(namedTempTarGzFile.name).extractall(directory.path)
        directory.scan()

        # CHECK
        pgkName, pkgVersion = PluginSwInstallManagerABC.getPackageInfo(directory)

        # CHECK
        pluginPackageFile = self._getFileForFileName(PLUGIN_PACKAGE_JSON, directory)

        # Example
        """
        {
          "title": "Peek App - Noop",
          "packageName": "plugin_noop",
          "company": "Synerty Pty Ltd",
          "website": "www.synerty.com",
          "version": "#PLUGIN_VER#",
          "buildNumber": "#PLUGIN_BUILD#",
          "buildDate": "#BUILD_DATE#"
        }
        """

        peekAppInfo = PeekPluginInfo()
        peekAppInfo.fileName = "%s.tar.gz" % dirName
        peekAppInfo.dirName = dirName

        packageJson = jsoncfg.load_config(pluginPackageFile.realPath)

        peekAppInfo.title = packageJson.plugin.title(require_string)
        peekAppInfo.name = packageJson.plugin.packageName(require_string)
        peekAppInfo.creator = packageJson.plugin.creator(require_string)
        peekAppInfo.website = packageJson.plugin.website(require_string)
        peekAppInfo.version = packageJson.plugin.version(require_string)
        peekAppInfo.buildNumber = packageJson.plugin.buildNumber(require_string)
        peekAppInfo.buildDate = packageJson.plugin.buildDate(require_string)

        del packageJson  # No longer used

        packageName = peekAppInfo.name

        # CHECK
        # Ensure that the python package name starts with "peek_plugin_"
        if not packageName.startswith("peek_plugin_"):
            raise Exception("papp_package.json plugin.packageName must start with"
                            " 'peek_plugin_',"
                            " It's '%s'" % packageName)

        # CHECK
        if packageName.replace("_", "-") != pgkName:
            raise Exception("PyPI package name VS papp_package.json plugin.packageName"
                            " mismatch, python package name underscores are replaced"
                            " with hyphens to match the PyPI package name"
                            " %s(%s) VS %s"
                            % (packageName.replace("_", "-"), packageName, pgkName))

        self._testPackageUpdate(namedTempTarGzFile.name, packageName)

        # CHECK
        # if pluginPackageFile.path != os.path.join(dirName, pgkName):
        #     raise Exception("Expected %s to be at %s, it's at %s"
        #                     % (PLUGIN_PACKAGE_JSON, dirName, pluginPackageFile.path))

        # CHECK
        if not dirName.startswith(pgkName):
            raise Exception("Peek app name '%s' does not match peek root dir name '%s"
                            % (packageName, dirName))

        # CHECK
        if peekAppInfo.version != pkgVersion:
            raise Exception("PyPI package version VS papp_package.json plugin.version"
                            " mismatch. %s VS %s"
                            % (peekAppInfo.version, pkgVersion))

        # Install the TAR file
        fullNewTarPath = os.path.join(PeekPlatformConfig.config.pluginSoftwarePath,
                                      peekAppInfo.fileName)

        shutil.copy(namedTempTarGzFile.name, fullNewTarPath)

        from peek_server.storage import dbConn
        session = dbConn.ormSession
        existing = (session.query(PeekPluginInfo)
                    .filter(PeekPluginInfo.name == peekAppInfo.name,
                            PeekPluginInfo.version == peekAppInfo.version)
                    .all())
        if existing:
            peekAppInfo.id = existing[0].id
            session.merge(peekAppInfo)
        else:
            session.add(peekAppInfo)

        session.commit()
        session.expunge_all()
        session.close()

        return packageName, pkgVersion, fullNewTarPath

    def _getFileForFileName(self, fileName: str, directory: Directory) -> File:
        """ Get File For FileName

        Get the file from the directory that matches the fileName, this directory
         contains the extracted package.

        :param fileName: The filename to look for.
        :param directory: The directory object where the package is extracted to.
        :return: The File object representing the PKG-INFO

        """
        files = [f for f in directory.files if f.name == fileName]

        if len(files) != 1:
            raise Exception("Uploaded package does not contain exatly 1 %s file, found %s"
                            % (fileName, len(files)))

        return files[0]

    def _testPackageUpdate(self, fileName: str, packageName: str) -> None:
        """ Test Package Update

        :param fileName: The full path to the package file to test install
        :param packageName: The name of the python package to try loading.
            EG "peek_plugin_noop"

        Since we ARE running on the server, we will test install these packages here
         first, this is done by creating a virtualenv.

        Currently we just use pip to try and install the package off line, if it's happy
         we're happy.

        """

        # Create the test virtualenv
        virtualEnvDir = Directory()

        virtExec = os.path.join(os.path.dirname(sys.executable), "virtualenv")
        virtArgsList = [virtExec,
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

        pipExec = os.path.join(virtualEnvDir.path, 'bin', 'pip')

        # Install all the packages from the directory
        pipArgs = [pipExec] + PluginSwInstallManagerABC.makePipArgs(fileName)
        pipArgs = ' '.join(pipArgs)

        try:
            spawnPty(pipArgs)

        except Exception as e:
            logSpawnException(e)

            # Update the detail of the exception and raise it
            raise Exception("Test install of updated plugin package failed.")

        # CHECK
        # Now try to load the package name
        #### This didn't load from the virtualenv...
        # modSpec = find_spec(packageName)
        # if not modSpec:
        #     raise Exception("Testing python import of %s failed, package not found"
        #                     % packageName)

        # Continue normally if it all succeeded
        logger.debug("Peek Plugin package update successfully tested.")
