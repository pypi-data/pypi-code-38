from abc import abstractproperty, ABCMeta

from celery.app.base import Celery


class PluginServerWorkerEntryHookABC(metaclass=ABCMeta):
    @abstractproperty
    def celeryApp(self) -> Celery:
        """ Celery App

        This plugin property is called by the platform when the server is initialising
        the plugin.

        The instance of the celery app returned by this property will be configured,
        allowing tasks linked to it to work with the Peek celerty task queues.

        :return: An instance of C{celery.app.base.Celery}

        Example code
        ------------
        ::

            from peek_plugin_noop.worker.NoopCeleryApp import celeryApp
            return celeryApp


        """
        pass
