from zope.interface import Interface


class INotificationSubscriptions(Interface):
    def get():
        """
        Get all explicit subscriptions for a given context
        """

    def add_notifications(userid):
        """
        Enable notifications for userid
        """

    def del_notifications(userid):
        """
        Disable previously added notifications
        """


class INotificationUnsubscriptions(Interface):

    def get():
        """
        Get all explicit users unsubscribed from receiving
        notifications in a given context
        """

    def get_user_data(userid):
        """
        Get unsubscription information for one user
        """

    def unsubscribe(userid):
        """
        Unsubscribe user from receiving notifications
        """

    def delete_unsubscribe(userid):
        """
        Delete the unsubscription from receiving notifications for a user
        """
