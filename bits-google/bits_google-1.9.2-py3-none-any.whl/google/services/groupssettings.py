"""Google Groups Settings API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class GroupsSettings(Base):
    """GroupsSettings class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.groupssettings = build('groupssettings', 'v1', credentials=credentials)

        self.defaults = {
            # Set up default group settings that won't change
            'allowExternalMembers': 'true',
            'allowGoogleCommunication': 'false',
            'allowWebPosting': 'true',
            'archiveOnly': 'false',
            # 'customFooterText': '',
            'customReplyTo': '',
            'defaultMessageDenyNotificationText': '',
            'description': '',  # This will need to be filled in with 'alias'
            # 'email': '',
            # 'includeCustomFooter': '',
            'isArchived': 'true',
            'maxMessageBytes': '25166000',  # default to 24M
            'membersCanPostAsTheGroup': 'false',
            'messageDisplayFont': 'DEFAULT_FONT',
            'messageModerationLevel': 'MODERATE_NON_MEMBERS',
            # 'name': '',
            'replyTo': 'REPLY_TO_SENDER',
            'sendMessageDenyNotification': 'false',
            'showInGroupDirectory': 'true',
            # 'spamModerationLevel': '',
            # 'whoCanAdd': '',
            # 'whoCanContactOwner': '',
            'whoCanInvite': 'ALL_MANAGERS_CAN_INVITE',
            'whoCanJoin': 'CAN_REQUEST_TO_JOIN',
            # 'whoCanLeaveGroup': '',
            'whoCanPostMessage': 'ANYONE_CAN_POST',
            'whoCanViewGroup': 'ALL_MEMBERS_CAN_VIEW',
            'whoCanViewMembership': 'ALL_MEMBERS_CAN_VIEW',
        }

    def get_defaults(self):
        """Return groupssettings defaults."""
        return self.defaults

    def get_group_settings(self, groupKey):
        """Return settings for a group."""
        return self.groupssettings.groups().get(groupUniqueId=groupKey).execute()

    def update_group_settings(self, groupKey, settings):
        """Update settings for a group."""
        params = {
            'groupUniqueId': groupKey,
            'body': settings,
        }
        return self.groupssettings.groups().update(**params).execute()
