

class AbstractNotification(object):
    def show_message(self, title, message):
        """
        Show message in the notification system of the OS.

        Parameters:
            title: The title of the notification.
            message: The notification message.
        """
        raise NotImplementedError()
