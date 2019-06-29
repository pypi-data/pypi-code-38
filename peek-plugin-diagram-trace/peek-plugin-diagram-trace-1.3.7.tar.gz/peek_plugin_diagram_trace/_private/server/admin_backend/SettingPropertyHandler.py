import logging

from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

from peek_plugin_diagram_trace._private.PluginNames import diagramTraceFilt
from peek_plugin_diagram_trace._private.storage.Setting import SettingProperty, \
    globalSetting

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.SettingProperty"}
filtKey.update(diagramTraceFilt)


# This is the CRUD handler
class __CrudHandler(OrmCrudHandler):
    # The UI only edits the global settings
    # You could get more complicated and have the UI edit different groups of settings.
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting(session).propertyObjects]


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """ Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleObservable):
        OrmCrudHandlerExtension.__init__(self)
        self._tupleObservable = tupleObservable

    def _tellObserver(self, tuple_, tuples, session, payloadFilt):
        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(SettingProperty.tupleName(), {})
        )
        return True

    afterUpdateCommit = _tellObserver


# This method creates an instance of the handler class.
def makeSettingPropertyHandler(dbSessionCreator,
                               tupleObservable: TupleDataObservableHandler):
    handler = __CrudHandler(dbSessionCreator, SettingProperty,
                            filtKey, retreiveAll=True)

    handler.addExtension(SettingProperty, __ExtUpdateObservable(tupleObservable))

    return handler
