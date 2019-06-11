

class ErrorNotification:

    def __init__(self):
        self.errors = []

    def notify_error(self,error):
        self.errors.append(error)

    def collect_notifications(self, notification):
        for error in notification.iterate_errors():
            self.notify_error(error)

    def iterate_errors(self):
        for error in self.errors:
            yield error

    def has_errors(self):
        return len(self.errors) > 0

