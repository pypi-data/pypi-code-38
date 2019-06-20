import re

from slackclient import SlackClient

from probator.config import dbconfig
from probator.constants import RGX_EMAIL_VALIDATION_PATTERN, ConfigOption
from probator.exceptions import SlackError
from probator.plugins.notifiers import BaseNotifier
from probator.utils import NotificationContact, send_notification, deprecated
from slackclient.exceptions import SlackClientError


class SlackNotifier(BaseNotifier):
    name = 'Slack Notifier'
    ns = 'notifier_slack'
    notifier_type = 'slack'
    validation = rf'^(#[a-zA-Z0-9\-_]+|{RGX_EMAIL_VALIDATION_PATTERN})$'
    options = (
        ConfigOption('enabled', False, 'bool', 'Enable the Slack notifier plugin'),
        ConfigOption('api_key', '', 'string', 'API token for the slack notifications'),
        ConfigOption('bot_name', 'Probator', 'string', 'Name of the bot in Slack'),
        ConfigOption('bot_color', '#607d8b', 'string', 'Hex formatted color code for notifications'),
    )

    def __init__(self, api_key=None):
        super().__init__()

        if not self.enabled:
            raise SlackError('Slack messaging is disabled')

        self.slack_client = SlackClient(api_key or dbconfig.get('api_key', self.ns))
        self.bot_name = dbconfig.get('bot_name', self.ns)
        self.color = dbconfig.get('bot_color', self.ns)

        if not self._check_credentials():
            raise SlackError('Failed authenticating to the slack api. Please check the API is valid')

    def _check_credentials(self):
        try:
            response = self.slack_client.api_call('auth.test')
            return response['ok']

        except SlackClientError:
            return False

    def _get_user_id_by_email(self, email):
        try:
            response = self.slack_client.api_call('users.list')

            if not response['ok']:
                raise SlackError(f'Failed to list Slack users: {response["error"]}')

            user = list(filter(lambda x: x['profile'].get('email') == email, response['members']))
            if user:
                return user.pop()['id']
            else:
                SlackError('Failed to get user from Slack!')

        except SlackClientError as ex:
            raise SlackError(ex)

    def _get_channel_for_user(self, user_email):
        user_id = self._get_user_id_by_email(user_email)
        try:
            response = self.slack_client.api_call('im.open', user=user_id)

            if not response['ok']:
                raise SlackError(f'Failed to get channel for user: {response["error"]}')

            return response['channel']['id']
        except Exception as ex:
            raise SlackError(ex)

    def _send_message(self, target_type, target, message, title):
        if target_type == 'user':
            channel = self._get_channel_for_user(target)
        else:
            channel = target

        response = self.slack_client.api_call(
            'chat.postMessage',
            channel=channel,
            attachments=[
                {
                    'fallback': message,
                    'color': self.color,
                    'title': title,
                    'text': message
                }
            ],
            username=self.bot_name
        )

        if not response.get('ok', False):
            raise SlackError(f'Failed to send message: {response["error"]}')

    def notify(self, subsystem, recipient, subject, body_html, body_text):
        """You can send messages either to channels and private groups by using the following formats

        #channel-name
        @username-direct-message

        Args:
            subsystem (`str`): Name of the subsystem originating the notification
            recipient (`str`): Recipient
            subject (`str`): Subject / title of the notification, not used for this notifier
            body_html (`str`): HTML formatted version of the message
            body_text (`str`): Text formatted version of the message

        Returns:
            `None`
        """
        if not re.match(self.validation, recipient, re.I):
            raise ValueError('Invalid recipient provided')

        if recipient.startswith('#'):
            target_type = 'channel'

        elif recipient.find('@') != -1:
            target_type = 'user'

        else:
            self.log.error(f'Unknown contact type for Slack: {recipient}')
            return

        try:
            self._send_message(
                target_type=target_type,
                target=recipient,
                message=body_text,
                title=subject
            )
        except SlackError as ex:
            self.log.error(f'Failed sending message to {recipient}: {ex}')

    @staticmethod
    @deprecated('send_message has been deprecated, use probator.utils.send_notifications instead')
    def send_message(contacts, message):
        """List of contacts the send the message to. You can send messages either to channels and private groups by
        using the following formats

        #channel-name
        @username-direct-message

        If the channel is the name of a private group / channel, you must first invite the bot to the channel to ensure
        it is allowed to send messages to the group.

        Returns true if the message was sent, else `False`

        Args:
            contacts (:obj:`list` of `str`,`str`): List of contacts
            message (str): Message to send

        Returns:
            `bool`
        """
        if type(contacts) == str:
            contacts = [contacts]

        recipients = list(set(contacts))

        send_notification(
            subsystem='UNKNOWN',
            recipients=[NotificationContact('slack', x) for x in recipients],
            subject='',
            body_html=message,
            body_text=message
        )
