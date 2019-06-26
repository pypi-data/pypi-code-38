import os
import platform
from ievv_opensource.utils.desktopnotifications import osxnotification
from ievv_opensource.utils.desktopnotifications import linuxnotification
from ievv_opensource.utils.desktopnotifications import mocknotification


if platform.system().lower() == 'darwin':
    _notificationbackend = osxnotification.Notification()
elif platform.system().lower() == 'linux':
    _notificationbackend = linuxnotification.Notification()
else:
    _notificationbackend = mocknotification.Notification()


def show_message(title, message):
    """
    Show a message in the desktop notification system of the OS.

    Examples::

        Show a message::

            desktopnotificationapi.show_message(
                title='Hello world',
                message='This is a test')

    Args:
        title (str): The title of the notification.
        message (str): The notification message.
    """
    enabled = os.environ.get('IEVV_OPENSOURCE_ENABLE_DESKTOP_NOTIFICATIONS', 'true')
    if enabled.lower() == 'true':
        _notificationbackend.show_message(title=title, message=message)


# if __name__ == '__main__':
#     show_message('Hello world', 'Testing "d\'s\'ad')
