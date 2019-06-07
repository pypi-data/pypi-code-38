from egcg_core.app_logging import AppLogger


class Notification(AppLogger):
    def __init__(self, name):
        self.name = name

    def notify(self, msg, attachments=None):
        raise NotImplementedError
