from Homevee.Item.Logic.Action import Action
from Homevee.Utils.Database import Database
from Homevee.Utils.NotificationManager import NotificationManager


class PushNotificationAction(Action):
    def __init__(self, users, msg):
        super(PushNotificationAction, self).__init__()
        self.users = users
        self.msg = msg

    def run(self):
        NotificationManager().send_notification_to_users(self.users, "Homevee", self.msg, Database())

    @staticmethod
    def get_from_dict(dict):
        try:
            users = dict['users']
            msg = dict['msg']
            return PushNotificationAction(users, msg)
        except:
            return None