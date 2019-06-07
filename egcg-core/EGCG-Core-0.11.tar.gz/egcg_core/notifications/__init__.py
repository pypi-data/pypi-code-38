import sys
import traceback
from egcg_core.app_logging import AppLogger
from egcg_core.config import cfg
from egcg_core.exceptions import EGCGError
from .asana import AsanaNotification
from .email import EmailNotification, EmailSender, send_email, send_html_email, send_plain_text_email
from .log import LogNotification


class NotificationCentre(AppLogger):
    ntf_aliases = {
        'log': LogNotification,
        'email': EmailNotification,
        'asana': AsanaNotification
    }

    def __init__(self, name):
        self.name = name
        self.subscribers = {}

        for k, v in cfg.get('notifications', {}).items():
            if k in self.ntf_aliases:
                self.debug('Configuring notification for: ' + k)
                self.subscribers[k] = self.ntf_aliases[k](name=self.name, **v)
            else:
                self.warning("Bad notification config '%s' - this will be ignored", k)

    def notify(self, msg, subs):
        exceptions = []
        for s in subs:
            if s in self.subscribers:
                try:
                    self.subscribers[s].notify(msg)
                except Exception as e:
                    etype, value, tb = sys.exc_info()
                    stacktrace = ''.join(traceback.format_exception(etype, value, tb))
                    self.critical(stacktrace)
                    exceptions.append(e)
            else:
                self.debug('Tried to notify by %s, but no configuration present', s)

        if exceptions:
            raise EGCGError(
                'Encountered the following errors during notification: %s' % ', '.join(
                    '%s: %s' % (e.__class__.__name__, str(e))
                    for e in exceptions
                )
            )

    def notify_all(self, msg):
        self.notify(msg, self.subscribers.keys())
