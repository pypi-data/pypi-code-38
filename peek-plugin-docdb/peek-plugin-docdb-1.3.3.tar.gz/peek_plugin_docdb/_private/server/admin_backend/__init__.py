from peek_plugin_docdb._private.server.admin_backend.EditDocumentPropertyHandler import \
    makeDocumentPropertyHandler
from peek_plugin_docdb._private.server.admin_backend.EditDocumentTypeHandler import \
    makeDocumentTypeHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from .ViewDocumentHandler import makeDocumentTableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeDocumentTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)

    yield makeDocumentPropertyHandler(tupleObservable, dbSessionCreator)

    yield makeDocumentTypeHandler(tupleObservable, dbSessionCreator)
