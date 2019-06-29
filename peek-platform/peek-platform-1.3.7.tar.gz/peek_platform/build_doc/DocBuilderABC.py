import logging
from typing import List

import os
import shutil
from collections import namedtuple

from peek_platform.build_common.BuilderABC import BuilderABC
from peek_platform.build_frontend.FrontendFileSync import FrontendFileSync
from peek_plugin_base.PluginPackageFileConfig import PluginPackageFileConfig

logger = logging.getLogger(__name__)

PluginDocDetail = namedtuple("PluginDocDetail",
                             ["pluginRootDir",
                              "pluginName",
                              "pluginTitle",
                              "docDir",
                              "docRst",
                              "hasApi"])

_mainTocTemplate = ''' 

.. toctree::
    :maxdepth: 3
    :caption: Contents:


'''

_tocTemplate = ''' 
   
.. toctree::
    :maxdepth: 2
    :caption: Contents:
    
'''

_confPluginsTemplate = '''

def load(createApiDocsFunc):
    """ Load
        
        Create APIs with the AutoAPI hack above
    """

'''

_confPluginsTemplatePart = '''
    import %s
    createApiDocsFunc(%s.__file__)
    
'''


class DocBuilderABC(BuilderABC):
    """ Peek Documentation Builder Mixin

    This class is used for the client and server.

    This class contains the logic for:
        * Linking in the sphinx documentation into the peek-doc-user, peek-doc-admin
            or peek-doc-dev projects
        * Compiling the documentation

    """

    def __init__(self, docProjectDir: str,
                 platformService: str,
                 jsonCfg,
                 loadedPlugins: List):
        assert platformService in ("peek-doc-user", "peek-doc-admin", "peek-doc-dev"), (
                "Unexpected service %s" % platformService)

        self._platformService = platformService
        self._docProjectDir = docProjectDir
        self._jsonCfg = jsonCfg
        self._loadedPlugins = loadedPlugins

        self._configKey = platformService.replace("peek-", "")

        if not os.path.isdir(docProjectDir):
            raise Exception("%s doesn't exist" % docProjectDir)

        self.fileSync = FrontendFileSync(lambda f, c: self._syncFileHook(f, c))
        self._dirSyncMap = list()

    def _loadPluginConfigs(self) -> [PluginDocDetail]:
        pluginDetails = []

        for plugin in self._loadedPlugins:
            assert isinstance(plugin.packageCfg, PluginPackageFileConfig)
            pluginPackageConfig = plugin.packageCfg.config

            if not self._configKey in pluginPackageConfig.requiresServices([]):
                continue

            if not self._configKey in pluginPackageConfig:
                logger.info("Skipping doc build for %s,"
                            "missing config section for %s",
                            plugin.name, self._platformService)
                continue

            jsonCfgNode = pluginPackageConfig[self._configKey]

            docDir = jsonCfgNode.docDir(None)
            docRst = jsonCfgNode.docRst(None)
            hasApi = jsonCfgNode.hasApi(False)

            pluginDetails.append(
                PluginDocDetail(pluginRootDir=plugin.rootDir,
                                pluginName=plugin.name,
                                pluginTitle=plugin.title,
                                docDir=docDir,
                                docRst=docRst,
                                hasApi=hasApi)
            )

        pluginDetails.sort(key=lambda x: x.pluginName)
        return pluginDetails

    def _writePluginsToc(self, docDir: str, pluginDetails: [PluginDocDetail]) -> None:

        contents = _mainTocTemplate

        for pluginDetail in pluginDetails:

            hasIndex = pluginDetail.docDir and pluginDetail.docRst
            hasApi = pluginDetail.hasApi

            if not (hasIndex or hasApi):
                continue
            contents += "    %s_toc\n" % pluginDetail.pluginName

        self._writeFileIfRequired(docDir, 'plugin_toc.rst', contents)

    def _writePluginToc(self, docDir: str, pluginDetails: [PluginDocDetail]) -> None:

        for pluginDetail in pluginDetails:
            hasIndex = pluginDetail.docDir and pluginDetail.docRst
            hasApi = pluginDetail.hasApi

            if not (hasApi or hasIndex):
                continue

            contents = pluginDetail.pluginTitle + "\n"
            contents += "+" * len(pluginDetail.pluginTitle) + "\n"

            contents += _tocTemplate

            if hasIndex:
                contents += "    %s/%s\n" % (
                    pluginDetail.pluginName, pluginDetail.docRst.replace(".rst", "")
                )

            if hasApi:
                contents += "    %s_api/%s\n" % (
                    pluginDetail.pluginName, pluginDetail.pluginName
                )

            contents += "\n\n"

            self._writeFileIfRequired(docDir, '%s_toc.rst' % pluginDetail.pluginName,
                                      contents)

    def _writePluginsApiConf(self, docDir: str, pluginDetails: [PluginDocDetail]) -> None:

        contents = _confPluginsTemplate

        for pluginDetail in pluginDetails:
            if not pluginDetail.hasApi:
                continue

            contents += _confPluginsTemplatePart % (
                pluginDetail.pluginName, pluginDetail.pluginName
            )

        self._writeFileIfRequired(docDir, 'plugin_api_conf.py', contents)

    def _writePluginsApiList(self, docDir: str, pluginDetails: [PluginDocDetail]) -> None:

        contents = ""

        for pluginDetail in pluginDetails:
            if not pluginDetail.hasApi:
                continue

            contents += pluginDetail.pluginName + "\n"

        self._writeFileIfRequired(docDir, 'plugin_api_list.txt', contents)

    def _syncPluginFiles(self, targetDir: str,
                         pluginDetails: [PluginDocDetail],
                         excludeFilesRegex=()) -> None:

        if not os.path.exists(targetDir):
            os.mkdir(targetDir)  # The parent must exist

        # Make a note of the existing items
        currentItems = set()
        createdItems = set()
        for item in os.listdir(targetDir):
            # We're only dealing with directories
            if not os.path.isdir(os.path.join(targetDir, item)):
                continue
            if item.startswith("peek_plugin_") or item.startswith("peek_core_"):
                currentItems.add(item)

        for pluginDetail in pluginDetails:
            if not pluginDetail.docDir:
                continue

            srcDir = os.path.join(pluginDetail.pluginRootDir, pluginDetail.docDir)
            if not os.path.exists(srcDir):
                logger.warning("%s doc dir %s doesn't exist",
                               pluginDetail.pluginName, pluginDetail.docDir)
                continue

            createdItems.add(pluginDetail.pluginName)

            linkPath = os.path.join(targetDir, pluginDetail.pluginName)
            self.fileSync.addSyncMapping(srcDir, linkPath,
                                         excludeFilesRegex=excludeFilesRegex)

        # Delete the items that we didn't create
        for item in currentItems - createdItems:
            path = os.path.join(targetDir, item)
            if os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
