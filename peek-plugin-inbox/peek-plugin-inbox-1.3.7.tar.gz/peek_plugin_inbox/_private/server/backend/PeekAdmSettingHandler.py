'''
Created on 09/07/2014

@author: synerty
'''
import txhttputil
from peek_plugin_inbox._private.PluginNames import inboxFilt

from peek_plugin_inbox._private.storage import Setting
from peek_plugin_inbox._private.storage.Setting import globalSetting
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

filtKey = {"key": "server.setting.data"}
filtKey.update(inboxFilt)


# HANDLER
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting(session).propertyObjects]

    # def postProcess(self, action, payloadFilt, vortexUuid):
    #     if action in [OrmCrudHandler.UPDATE, OrmCrudHandler.CREATE]:
    #         settings = globalSetting()
    #         txhttputil.DESCRIPTION = settings[Setting.SYSTEM_DESCRIPTION]
    #         txhttputil.TITLE = settings[Setting.SYSTEM_NAME]


def createAdminSettingsHandler(dbSessionCreator):
    return __CrudHandler(dbSessionCreator, Setting, filtKey)
