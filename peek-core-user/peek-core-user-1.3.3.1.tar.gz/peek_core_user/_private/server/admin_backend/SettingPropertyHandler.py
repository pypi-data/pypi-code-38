import logging

from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.storage.Setting import SettingProperty, globalSetting, \
    ldapSetting
from peek_core_user._private.tuples.UserLoginUiSettingTuple import UserLoginUiSettingTuple

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


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """ Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def _afterCommit(self, tuple_, tuples, session, payloadFilt):
        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(UserLoginUiSettingTuple.tupleName(), {})
        )
        return True

    afterUpdateCommit = _afterCommit
    afterDeleteCommit = _afterCommit


# This method creates an instance of the handler class.
def makeSettingPropertyHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, SettingProperty,
                            filtKey, retreiveAll=True)
    handler.addExtension(SettingProperty, __ExtUpdateObservable(tupleObservable))

    logger.debug("Started")
    return handler
