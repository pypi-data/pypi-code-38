import os
from ievv_opensource.utils.desktopnotifications.base import AbstractNotification

try:
    from shlex import quote
except ImportError:
    from pipes import quote


class Notification(AbstractNotification):
    def show_message(self, title, message):
        os.system('notify-send {} {}'.format(quote(title), quote(message)))
