import os
from ievv_opensource.utils.desktopnotifications.base import AbstractNotification

try:
    from shlex import quote
except ImportError:
    from pipes import quote


class Notification(AbstractNotification):
    def show_message(self, title, message):
        command = 'display notification "{message}" with title "{title}"'.format(
            title=title.replace('"', "'"),
            message=message.replace('"', "'"))
        os.system('osascript -e {}'.format(quote(command)))
