import logging

logger = logging.getLogger(__name__)


class ObjectLogger(logging.LoggerAdapter):
    """ An utility to prefix the per-object log messages. """

    def __init__(self, body):
        self._uid = body.get('metadata', {}).get('uid')
        self._name = body.get('metadata', {}).get('name', self._uid)
        self._namespace = body.get('metadata', {}).get('namespace', 'default')
        super().__init__(
            logger,
            extra=dict(
                uid=self._uid,
                name=self._name,
                namespace=self._namespace,
            ),
        )

    def process(self, msg, kwargs):
        return f"[{self._namespace}/{self._name}] {msg}", kwargs
