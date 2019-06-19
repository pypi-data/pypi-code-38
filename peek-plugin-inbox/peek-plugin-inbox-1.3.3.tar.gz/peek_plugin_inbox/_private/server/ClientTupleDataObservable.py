import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_inbox._private.PluginNames import inboxFilt, \
    inboxObservableName
from peek_plugin_inbox._private.server.tuple_providers.ActivityTupleProvider import \
    ActivityTupleProvider
from peek_plugin_inbox._private.storage.Activity import Activity
from peek_plugin_inbox._private.storage.Task import Task
from .tuple_providers.TaskTupleProvider import TaskTupleProvider

logger = logging.getLogger(__name__)


def makeTupleDataObservableHandler(ormSessionCreator):
    observable = TupleDataObservableHandler(observableName=inboxObservableName,
                                            additionalFilt=inboxFilt)

    observable.addTupleProvider(Task.tupleName(), TaskTupleProvider(ormSessionCreator))

    observable.addTupleProvider(Activity.tupleName(),
                                ActivityTupleProvider(ormSessionCreator))
    return observable
