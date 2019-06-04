# https://github.com/olucurious/PyFCM

from Homevee.Helper.HomeveeCloud import HomeveeCloudWrapper
from Homevee.Item.User import User
from Homevee.Utils.Database import Database


class NotificationManager():
    def __init__(self):
        return

    def send_notification(self, registration_ids: list, message_title: str,
                          message_body: str, click_action: dict = None):
        """
        Sends a notification to the ids
        :param registration_ids: the recipients ids
        :param message_title: the title of the notification
        :param message_body: the body of the notification
        :param click_action: the on-click action
        :return:
        """
        cloud_wrapper = HomeveeCloudWrapper()
        message_data = {'title': message_title, 'msg': message_body, 'clickaction': click_action}
        cloud_wrapper.send_push_notification(registration_ids, message_data)

    def send_notification_to_users(self, users: list, message_title: str, message_body: str,
                                   db: Database = None, click_action: str = None):
        """
        Sends a notification to the given users
        :param users: list of users
        :param message_title: the title of the message
        :param message_title: the title of the notification
        :param message_body: the body of the notification
        :param click_action: the on-click action
        :return:
        """
        registration_ids = self.get_user_tokens(users, db)
        self.send_notification(registration_ids, message_title, message_body, click_action)

    def send_notification_to_admin(self, message_title: str, message_body: str, db: Database,
                                   click_action: str = None):
        """
        Sends a notification to all admins
        :param message_title: the title of the message
        :param message_title: the title of the notification
        :param message_body: the body of the notification
        :param click_action: the on-click action
        :return:
        """
        admins = User.load_by_permission("admin", db)
        self.send_notification_to_users(admins, message_title, message_body, db, click_action)

    def get_user_tokens(self, users, db: Database = None):
        if db is None:
            db = Database()
        """
        Gets the users tokens
        :param users: the users
        :param db: the database connection
        :return: the list of tokens
        """
        tokens = []

        if users is None or (len(users) is 0):
            items = db.select_all("SELECT TOKEN FROM PUSH_NOTIFICATION_TOKENS", None)

            for item in items():
                tokens.append(item['TOKEN'])
        else:
            for user in users:
                item = db.select_one("SELECT TOKEN FROM PUSH_NOTIFICATION_TOKENS WHERE USERNAME = :user",
                            {'user': user})

                if (item['TOKEN'] is not None):
                    tokens.append(item['TOKEN'])

        return tokens

    def delete_user_tokens(self, username: str, db: Database = None):
        if db is None:
            db = Database()
        """
        Deletes the user token
        :param username: the user to delete the token from
        :param db: the database connection
        :return:
        """
        db.delete("DELETE FROM PUSH_NOTIFICATION_TOKENS WHERE USERNAME = :user", {'user': username})