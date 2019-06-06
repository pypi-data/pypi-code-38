import logging
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.storage.Setting import SettingProperty, globalSetting, \
    ldapSetting

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.SettingProperty"}
filtKey.update(userPluginFilt)


# This is the CRUD handler
class __CrudHandler(OrmCrudHandler):
    # The UI only edits the global settings
    # You could get more complicated and have the UI edit different groups of settings.
    def createDeclarative(self, session, payloadFilt):
        settingType = payloadFilt.get('settingType')
        if settingType == "Global":
            return [p for p in globalSetting(session).propertyObjects]
        elif settingType == 'LDAP':
            return [p for p in ldapSetting(session).propertyObjects]

        raise Exception("%s is not a known settings group" % settingType)


# This method creates an instance of the handler class.
def makeSettingPropertyHandler(dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, SettingProperty,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    return handler