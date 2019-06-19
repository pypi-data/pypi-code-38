import logging
from typing import List

import os

from peek_platform.build_frontend.FrontendBuilderABC import FrontendBuilderABC, BuildTypeEnum
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class NativescriptBuilder(FrontendBuilderABC):
    def __init__(self, frontendProjectDir: str, platformService: str,
                 jsonCfg, loadedPlugins: List):
        FrontendBuilderABC.__init__(self, frontendProjectDir, platformService,
                                    BuildTypeEnum.NATIVE_SCRIPT,
                                    jsonCfg, loadedPlugins)

    @deferToThreadWrapWithLogger(logger, checkMainThread=False)
    def build(self) -> None:
        if not self._jsonCfg.feNativescriptBuildPrepareEnabled:
            logger.info("SKIPPING, Nativescript build prepare is disabled in config")
            return

        excludeRegexp = (
            r'.*[.]web[.]ts$',
            r'.*[.]mweb[.]ts$',
            r'.*[.]dweb[.]ts$',
            r'.*[.]web[.]html$',
            r'.*[.]mweb[.]html$',
            r'.*[.]dweb[.]html$',
            r'.*[.]web[.]scss',
            r'.*[.]mweb[.]scss',
            r'.*[.]dweb[.]scss',
            r'.*__pycache__.*',
            r'.*[.]py$'
        )

        keepCompiledFilePatterns = {
            'ts': ['js.map', 'js'],
            'scss': ['css']
        }

        self._dirSyncMap = list()

        feBuildDir = os.path.join(self._frontendProjectDir, 'build-ns')
        feSrcAppDir = os.path.join(self._frontendProjectDir, 'src', 'app')

        feAppDir = os.path.join(feBuildDir, 'app')
        feAssetsDir = os.path.join(feBuildDir, 'app', 'assets')
        feNodeModDir = os.path.join(feBuildDir, 'node_modules')

        self._moduleCompileRequired = False
        self._moduleCompileLoopingCall = None

        feModuleDirs = [
            (os.path.join(feAppDir, '@peek'), "moduleDir"),
        ]

        pluginDetails = self._loadPluginConfigs()

        # --------------------
        # Check if node_modules exists

        # if not os.path.exists(os.path.join(feBuildDir, 'node_modules')):
        #     raise NotADirectoryError("node_modules doesn't exist, ensure you've run "
        #                              "`npm install` in dir %s" % feBuildDir)

        # --------------------
        # Prepare the common frontend application

        self.fileSync.addSyncMapping(feSrcAppDir,
                                     os.path.join(feAppDir, 'app'),
                                     keepCompiledFilePatterns=keepCompiledFilePatterns,
                                     excludeFilesRegex=excludeRegexp)

        # --------------------
        # Prepare the home and title bar configuration for the plugins
        self._writePluginHomeLinks(feAppDir, pluginDetails)
        self._writePluginTitleBarLinks(feAppDir, pluginDetails)
        self._writePluginConfigLinks(feAppDir, pluginDetails)

        # --------------------
        # Prepare the plugin lazy loaded part of the application
        self._writePluginAppRouteLazyLoads(feAppDir, pluginDetails)
        self._syncPluginFiles(feAppDir, pluginDetails, "appDir",
                              keepCompiledFilePatterns=keepCompiledFilePatterns,
                              excludeFilesRegex=excludeRegexp)

        # --------------------
        # Prepare the plugin lazy loaded part of the application
        self._writePluginCfgRouteLazyLoads(feAppDir, pluginDetails)
        self._syncPluginFiles(feAppDir, pluginDetails, "cfgDir",
                              isCfgDir=True,
                              keepCompiledFilePatterns=keepCompiledFilePatterns,
                              excludeFilesRegex=excludeRegexp)

        # --------------------
        # Prepare the plugin assets
        self._syncPluginFiles(feAssetsDir, pluginDetails, "assetDir",
                              excludeFilesRegex=excludeRegexp)

        # --------------------
        # Prepare the shared / global parts of the plugins

        self._writePluginRootModules(feAppDir, pluginDetails)
        self._writePluginRootServices(feAppDir, pluginDetails)
        self._writePluginRootComponents(feAppDir, pluginDetails)

        # There are two
        for feModDir, jsonAttr, in feModuleDirs:
            # Link the shared code, this allows plugins
            # * to import code from each other.
            # * provide global services.
            self._syncPluginFiles(feModDir, pluginDetails, jsonAttr,
                                  keepCompiledFilePatterns=keepCompiledFilePatterns,
                                  excludeFilesRegex=excludeRegexp)

        # Lastly, Allow the clients to override any frontend files they wish.
        # overlay src
        self.fileSync.addSyncMapping(self._jsonCfg.feFrontendSrcOverlayDir,
                                     feAppDir,
                                     parentMustExist=True,
                                     deleteExtraDstFiles=False,
                                     excludeFilesRegex=excludeRegexp)

        # overlay node_modules
        self.fileSync.addSyncMapping(self._jsonCfg.feFrontendNodeModuleOverlayDir,
                                     feNodeModDir,
                                     parentMustExist=True,
                                     deleteExtraDstFiles=False,
                                     excludeFilesRegex=excludeRegexp)

        self.fileSync.syncFiles()

        if self._jsonCfg.feSyncFilesForDebugEnabled:
            logger.info("Starting frontend development file sync")
            self.fileSync.startFileSyncWatcher()

    def stopDebugWatchers(self):
        logger.info("Stoping frontend development file sync")
        self.fileSync.stopFileSyncWatcher()

    def _syncFileHook(self, fileName: str, contents: bytes) -> bytes:
        if fileName.endswith(".ts"):
            contents = contents.replace(b'@synerty/peek-util/index.web',
                                        b'@synerty/peek-util/index.ns')
            contents = contents.replace(b'@synerty/peek-util/index.mweb',
                                        b'@synerty/peek-util/index.ns')

            # replace imports that end with .web/.mweb with .ns
            # This will allow platform dependent typescript modules,
            # EG photo taking modules
            contents = contents.replace(b'.mweb";', b'.ns";')
            contents = contents.replace(b'.web";', b'.ns";')

            # Update the @peek import to use the /app path
            contents = contents.replace(b'from "@peek/', b'from "~/@peek/')
            contents = contents.replace(b"from '@peek/", b"from '~/@peek/")

            # Occasionally @peek/peek_plugin_... will need to import from the lazy loaded
            # UI part of the module, This makes that possible
            # Update the @peek import to use the /app path
            contents = contents.replace(b'from "peek_', b'from "~/peek_')
            contents = contents.replace(b"from 'peek_", b"from '~/peek_")

            # Change the web peek-util references to NS peek util references
            contents = contents.replace(b'from "@synerty/peek-util-web',
                                        b'from "@synerty/peek-util-ns')
            contents = contents.replace(b"from '@synerty/peek-util-web",
                                        b"from '@synerty/peek-util-ns")

            # Fix up references to the lazy load routes
            contents = contents.replace(b"loadChildren: 'peek_",
                                        b"loadChildren: '~/peek_")
            contents = contents.replace(b'loadChildren: "peek_',
                                        b'loadChildren: "~/peek_')


            # if b'@NgModule' in contents:
            #     return self._patchModule(fileName, contents)

            if b'@Component' in contents:
                return self._patchComponent(fileName, contents)

        return contents

    # def _patchModule(self, fileName: str, contents: bytes) -> bytes:
    #     newContents = b''
    #     for line in contents.splitlines(True):
    #
    #         newContents += line
    #
    #     return newContents

    def _patchComponent(self, fileName: str, contents: bytes) -> bytes:
        """ Patch Component
        
        Apply patches to the WEB file to convert it to the NativeScript version

        :param fileName: The name of the file
        :param contents: The original contents of the file
        :return: The new contents of the file
        """
        inComponentHeader = False

        newContents = b''
        for line in contents.splitlines(True):
            if line.startswith(b"@Component"):
                inComponentHeader = True

            elif line.startswith(b"export"):
                inComponentHeader = False

            elif inComponentHeader:
                line = (line
                    .replace(b'.mweb.html', b'.ns.html')
                    .replace(b'.mweb.css', b'.ns.css')
                    .replace(b'.mweb.scss', b'.ns.scss')
                    .replace(b'.web.html', b'.ns.html')
                    .replace(b'.web.css', b'.ns.css')
                    .replace(b'.web.scss', b'.ns.scss')
                    .replace(b"'./", b"'")
                    )

            newContents += line

        return newContents
