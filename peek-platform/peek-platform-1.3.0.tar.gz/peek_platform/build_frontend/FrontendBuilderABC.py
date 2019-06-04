import json
import logging
from textwrap import dedent
from typing import List, Callable, Optional, Dict

import os
import shutil
from collections import namedtuple
from jsoncfg.value_mappers import require_bool

from peek_platform.build_common.BuilderABC import BuilderABC
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import \
    PeekFileConfigFrontendDirMixin
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.build_frontend.FrontendFileSync import FrontendFileSync
from peek_plugin_base.PluginPackageFileConfig import PluginPackageFileConfig

logger = logging.getLogger(__name__)

# Quiten the file watchdog
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.INFO)

PluginDetail = namedtuple("PluginDetail",
                          ["pluginRootDir",
                           "pluginName",
                           "pluginTitle",
                           "appDir",
                           "appModule",
                           "cfgDir",
                           "cfgModule",
                           "moduleDir",
                           "assetDir",
                           "rootModules",
                           "rootServices",
                           "icon",
                           "homeLinkText",
                           "showHomeLink",
                           "showInTitleBar",
                           "titleBarLeft",
                           "titleBarText",
                           "configLinkPath"])


class BuildTypeEnum:
    ELECTRON = "ELECTRON"
    WEB_DESKTOP = "WEB_DESKTOP"
    WEB_MOBILE = "WEB_MOBILE"
    WEB_ADMIN = "WEB_ADMIN"
    NATIVE_SCRIPT = "NATIVE_SCRIPT"


class FrontendBuilderABC(BuilderABC):
    """ Peek App Frontend Installer Mixin

    This class is used for the client and server.

    This class contains the logic for:
        * Linking in the frontend angular components to the frontend project
        * Compiling the frontend project

    :TODO: Use find/sort to generate a string of the files when this was last run.
        Only run it again if anything has changed.

    """

    _CFG_KEYS = {
        BuildTypeEnum.ELECTRON: ["desktop-electron", "desktop"],
        BuildTypeEnum.WEB_DESKTOP: ["desktop-web", "desktop"],
        BuildTypeEnum.WEB_MOBILE: ["mobile-web", "mobile"],
        BuildTypeEnum.NATIVE_SCRIPT: ["mobile-ns", "mobile"],
        BuildTypeEnum.WEB_ADMIN: ["admin"]
    }

    def __init__(self, frontendProjectDir: str, platformService: str,
                 buildType: BuildTypeEnum, jsonCfg,
                 loadedPlugins: List):
        assert platformService in ("peek-mobile", "peek-admin", "peek-desktop"), (
                "Unexpected service %s" % platformService)

        self._platformService = platformService
        self._buildType = buildType
        self._jsonCfg = jsonCfg
        self._frontendProjectDir = frontendProjectDir
        self._loadedPlugins = loadedPlugins

        if not isinstance(self._jsonCfg, PeekFileConfigFrontendDirMixin):
            raise Exception("The file config must inherit the"
                            " PeekFileConfigFrontendDirMixin")

        if not isinstance(self._jsonCfg, PeekFileConfigOsMixin):
            raise Exception("The file config must inherit the"
                            " PeekFileConfigOsMixin")

        if not os.path.isdir(frontendProjectDir):
            raise Exception("% doesn't exist" % frontendProjectDir)

        self.fileSync = FrontendFileSync(lambda f, c: self._syncFileHook(f, c))
        self._dirSyncMap = list()
        self._fileWatchdogObserver = None

    def _loadPluginConfigs(self) -> [PluginDetail]:
        pluginDetails = []

        for plugin in self._loadedPlugins:
            assert isinstance(plugin.packageCfg, PluginPackageFileConfig)
            pluginPackageConfig = plugin.packageCfg.config
            jsonCfgNode = None

            for configKey in self._CFG_KEYS[self._buildType]:
                if configKey in pluginPackageConfig:
                    jsonCfgNode = pluginPackageConfig[configKey]
                    break

            if not jsonCfgNode:
                logger.info("Skipping frontend build for %s,"
                            "missing config section for %s",
                            plugin.name, self._buildType)
                continue

            enabled = (jsonCfgNode.enableAngularFrontend(True, require_bool))

            if not enabled:
                continue

            appDir = jsonCfgNode.appDir(None)
            appModule = jsonCfgNode.appModule(None)

            cfgDir = jsonCfgNode.cfgDir(None)
            cfgModule = jsonCfgNode.cfgModule(None)

            moduleDir = jsonCfgNode.moduleDir(None)
            assetDir = jsonCfgNode.assetDir(None)

            showHomeLink = jsonCfgNode.showHomeLink(True)
            homeLinkText = jsonCfgNode.homeLinkText(plugin.title)
            showInTitleBar = jsonCfgNode.showInTitleBar(False)
            titleBarLeft = jsonCfgNode.titleBarLeft(False)
            titleBarText = jsonCfgNode.titleBarText(None)
            configLinkPath = jsonCfgNode.configLinkPath(None)

            def checkThing(name, data):
                sub = (name, plugin.name)
                if data:
                    assert data["file"], "%s.file is missing for %s" % sub
                    assert data["class"], "%s.class is missing for %s" % sub

                if not data.get("persistent"):
                    data["persistent"] = False

                data["useClassFile"] = data.get("useClassFile")
                data["useClassClass"] = data.get("useClassClass")

            # Root Modules
            rootModules = jsonCfgNode.rootModules([])
            for rootModule in rootModules:
                checkThing("rootModules", rootModule)

            # Root Services
            rootServices = jsonCfgNode.rootServices([])
            for rootService in rootServices:
                checkThing("rootServices", rootService)

            icon = (jsonCfgNode.icon(None))

            pluginDetails.append(
                PluginDetail(pluginRootDir=plugin.rootDir,
                             pluginName=plugin.name,
                             pluginTitle=plugin.title,
                             appDir=appDir,
                             appModule=appModule,
                             cfgDir=cfgDir,
                             cfgModule=cfgModule,
                             moduleDir=moduleDir,
                             assetDir=assetDir,
                             rootModules=rootModules,
                             rootServices=rootServices,
                             icon=icon,
                             homeLinkText=homeLinkText,
                             showHomeLink=showHomeLink,
                             showInTitleBar=showInTitleBar,
                             titleBarLeft=titleBarLeft,
                             titleBarText=titleBarText,
                             configLinkPath=configLinkPath)
            )

        pluginDetails.sort(key=lambda x: x.pluginName)
        return pluginDetails

    def _writePluginHomeLinks(self, feAppDir: str,
                              pluginDetails: [PluginDetail]) -> None:
        """
        export const homeLinks = [
            {
                name: 'plugin_noop',
                title: "Noop",
                resourcePath: "/peek_plugin_noop",
                pluginIconPath: "/peek_plugin_noop/home_icon.png"
            }
        ];
        """

        links = []
        for pluginDetail in pluginDetails:
            if not (pluginDetail.appModule and pluginDetail.showHomeLink):
                continue

            links.append(dict(name=pluginDetail.pluginName,
                              title=pluginDetail.homeLinkText,
                              resourcePath="/%s" % pluginDetail.pluginName,
                              pluginIconPath=pluginDetail.icon))

        links.sort(key=lambda item: item["title"])

        contents = "// This file is auto generated, the git version is blank and .gitignored\n"
        contents += "export const homeLinks = %s;\n" % json.dumps(
            links, sort_keys=True, indent=4, separators=(', ', ': '))

        self._writeFileIfRequired(feAppDir, 'plugin-home-links.ts', contents)

    def _writePluginConfigLinks(self, feAppDir: str,
                                pluginDetails: [PluginDetail]) -> None:
        """
        export const configLinks = [
            {
                name: 'plugin_noop',
                title: "Noop",
                resourcePath: "/peek_plugin_noop_cfg",
                pluginIconPath: "/assets/peek_plugin_noop/home_icon.png"
            }
        ];
        """

        links = []
        for pluginDetail in pluginDetails:
            if not pluginDetail.cfgModule:
                continue

            links.append(dict(name=pluginDetail.pluginName,
                              title=pluginDetail.homeLinkText,
                              resourcePath="/%s_cfg/" % pluginDetail.pluginName,
                              pluginIconPath=pluginDetail.icon))

        links.sort(key=lambda item: item["title"])

        contents = "// This file is auto generated, the git version is blank and .gitignored\n"
        contents += "export const configLinks = %s;\n" % json.dumps(
            links, sort_keys=True, indent=4, separators=(', ', ': '))

        self._writeFileIfRequired(feAppDir, 'plugin-config-links.ts', contents)

    def _writePluginTitleBarLinks(self, feAppDir: str,
                                  pluginDetails: [PluginDetail]) -> None:
        """
        
        import {TitleBarLink} from "@synerty/peek-util";

        export const titleBarLinks :TitleBarLink = [
            {
                plugin : "peek_plugin_noop",
                text: "Noop",
                left: false,
                resourcePath: "/peek_plugin_noop/home_icon.png",
                badgeCount : null
            }
        ];
        """

        links = []
        for pluginDetail in pluginDetails:
            if not (pluginDetail.appModule and pluginDetail.showInTitleBar):
                continue

            links.append(dict(plugin=pluginDetail.pluginName,
                              text=pluginDetail.titleBarText,
                              left=pluginDetail.titleBarLeft,
                              resourcePath="/%s" % pluginDetail.pluginName,
                              badgeCount=None))

        contents = "// This file is auto generated, the git version is blank and .gitignored\n\n"
        contents += "import {TitleBarLink} from '@synerty/peek-util';\n\n"
        contents += "export const titleBarLinks :TitleBarLink[] = %s;\n" % json.dumps(
            links, sort_keys=True, indent=4, separators=(', ', ': '))

        self._writeFileIfRequired(feAppDir, 'plugin-title-bar-links.ts', contents)

    def _writePluginAppRouteLazyLoads(self, feAppDir: str,
                                      pluginDetails: [PluginDetail]) -> None:
        _appRoutesTemplate = dedent("""
            {
                path: '%s',
                loadChildren: "%s/%s"
            }""")

        routes = []
        for pluginDetail in pluginDetails:
            if pluginDetail.appModule:
                routes.append(_appRoutesTemplate
                              % (pluginDetail.pluginName,
                                 pluginDetail.pluginName,
                                 pluginDetail.appModule))

        routeData = "// This file is auto generated, the git version is blank and .gitignored\n"
        routeData += "export const pluginAppRoutes = ["
        routeData += ",".join(routes)
        routeData += "\n];\n"

        self._writeFileIfRequired(feAppDir, 'plugin-app-routes.ts', routeData)

    def _writePluginCfgRouteLazyLoads(self, feAppDir: str,
                                      pluginDetails: [PluginDetail]) -> None:
        _cfgRoutesTemplate = dedent("""
            {
                path: '%s_cfg',
                loadChildren: "%s_cfg/%s"
            }""")

        routes = []
        for pluginDetail in pluginDetails:
            if pluginDetail.cfgModule:
                routes.append(_cfgRoutesTemplate
                              % (pluginDetail.pluginName,
                                 pluginDetail.pluginName,
                                 pluginDetail.cfgModule))

        routeData = "// This file is auto generated, the git version is blank and .gitignored\n"
        routeData += "export const pluginCfgRoutes = ["
        routeData += ",".join(routes)
        routeData += "\n];\n"

        self._writeFileIfRequired(feAppDir, 'plugin-cfg-routes.ts', routeData)

    def _writePluginRootModules(self, feAppDir: str,
                                pluginDetails: [PluginDetail]) -> None:

        # initiliase the arrays, and put in the persisten service module
        imports = ['''import {PluginRootServicePersistentLoadModule} 
                        from "./plugin-root-services";''']
        modules = ['PluginRootServicePersistentLoadModule']

        for pluginDetail in pluginDetails:
            for rootModule in pluginDetail.rootModules:
                imports.append('import {%s} from "@peek/%s/%s";'
                               % (rootModule["class"],
                                  pluginDetail.pluginName,
                                  rootModule["file"]))
                modules.append(rootModule["class"])

        routeData = "// This file is auto generated, the git version is blank and .gitignored\n"
        routeData += '\n'.join(imports) + '\n'
        routeData += "export const pluginRootModules = [\n\t"
        routeData += ",\n\t".join(modules)
        routeData += "\n];\n"

        self._writeFileIfRequired(feAppDir, 'plugin-root-modules.ts', routeData)

    def _writePluginRootServices(self, feAppDir: str,
                                 pluginDetails: [PluginDetail]) -> None:

        imports = []
        services = []
        persistentServices = []
        for pluginDetail in pluginDetails:
            for rootService in pluginDetail.rootServices:
                imports.append('import {%s} from "@peek/%s/%s";'
                               % (rootService["class"],
                                  pluginDetail.pluginName,
                                  rootService["file"]))

                if rootService["useClassFile"] and rootService["useClassClass"]:
                    imports.append('import {%s} from "@peek/%s/%s";'
                                   % (rootService["useClassClass"],
                                      pluginDetail.pluginName,
                                      rootService["useClassFile"]))
                    services.append(
                        '{provide:%s, useClass:%s}'
                        % (rootService["class"], rootService["useClassClass"])
                    )

                else:
                    services.append(rootService["class"])

                if rootService["persistent"]:
                    persistentServices.append(rootService["class"])

        routeData = "// This file is auto generated, the git version is blank and .gitignored\n"
        routeData += '\n'.join(imports) + '\n'
        routeData += "export const pluginRootServices = [\n\t"
        routeData += ",\n\t".join(services)
        routeData += "\n];\n"

        routeData += '''
        import {NgModule} from "@angular/core";

        @NgModule({
        
        })
        export class PluginRootServicePersistentLoadModule {
            constructor(%s){
        
            }
        
        }
        ''' % ', '.join(['private _%s:%s' % (s, s) for s in persistentServices])

        self._writeFileIfRequired(feAppDir, 'plugin-root-services.ts', routeData)

    def _syncPluginFiles(self, targetDir: str,
                         pluginDetails: [PluginDetail],
                         attrName: str,
                         preSyncCallback: Optional[Callable[[], None]] = None,
                         postSyncCallback: Optional[Callable[[], None]] = None,
                         keepCompiledFilePatterns: Optional[Dict[str, List[str]]] = None,
                         excludeFilesRegex=(),
                         isCfgDir=False) -> None:
        cfgPostfix = "_cfg"

        if not os.path.exists(targetDir):
            os.mkdir(targetDir)  # The parent must exist

        # Make a note of the existing items
        currentItems = set()
        createdItems = set()
        for item in os.listdir(targetDir):
            if not item.startswith("peek_plugin_") or item.startswith("peek_core_"):
                continue

            if isCfgDir:
                if item.endswith(cfgPostfix):
                    currentItems.add(item)
            else:
                if not item.endswith(cfgPostfix):
                    currentItems.add(item)

        for pluginDetail in pluginDetails:
            frontendDir = getattr(pluginDetail, attrName, None)
            if not frontendDir:
                continue

            srcDir = os.path.join(pluginDetail.pluginRootDir, frontendDir)
            if not os.path.exists(srcDir):
                logger.warning("%s FE dir %s doesn't exist",
                               pluginDetail.pluginName, frontendDir)
                continue

            if isCfgDir:
                createdItems.add(pluginDetail.pluginName + cfgPostfix)
                linkPath = os.path.join(targetDir, pluginDetail.pluginName + cfgPostfix)
            else:
                createdItems.add(pluginDetail.pluginName)
                linkPath = os.path.join(targetDir, pluginDetail.pluginName)

            self.fileSync.addSyncMapping(srcDir, linkPath,
                                         keepCompiledFilePatterns=keepCompiledFilePatterns,
                                         preSyncCallback=preSyncCallback,
                                         postSyncCallback=postSyncCallback,
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

    def _updatePackageJson(self, targetJson: str,
                           pluginDetails: [PluginDetail]) -> None:

        serviceName = "@peek"

        # Remove all the old symlinks

        with open(targetJson, 'r') as f:
            jsonData = json.load(f)

        dependencies = jsonData["dependencies"]
        for key in list(dependencies):
            if key.startswith(serviceName):
                del dependencies[key]

        for pluginDetail in pluginDetails:
            if not pluginDetail.moduleDir:
                continue

            moduleDir = os.path.join(pluginDetail.pluginRootDir,
                                     pluginDetail.moduleDir)

            name = "%s/%s" % (serviceName, pluginDetail.pluginName)
            dependencies[name] = "file:///" + moduleDir.replace("\\", '/')

        contents = json.dumps(jsonData, sort_keys=True, indent=2,
                              separators=(',', ': '))

        self._writeFileIfRequired(os.path.dirname(targetJson),
                                  os.path.basename(targetJson),
                                  contents)
