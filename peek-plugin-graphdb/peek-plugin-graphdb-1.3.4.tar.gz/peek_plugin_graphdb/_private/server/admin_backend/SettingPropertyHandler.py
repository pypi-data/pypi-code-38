import logging
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.Setting import SettingProperty, globalSetting

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.SettingProperty"}
filtKey.update(graphDbFilt)


# This is the CRUD handler
class __CrudHandler(OrmCrudHandler):
    # The UI only edits the global settings
    # You could get more complicated and have the UI edit different groups of settings.
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting(session).propertyObjects]


# This method creates an instance of the handler class.
def makeSettingPropertyHandler(dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, SettingProperty,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    return handler