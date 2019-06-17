from __future__ import annotations
from .exceptions import *

class Auth:
    def __init__(self, **kwargs) -> None:
        try:
            self.bot_username = kwargs['bot_username']
            self.oauth_token = kwargs['oauth_token']
        except:
            OneOfTheseKwargsNotProvided('"bot_username", "oauth_token"')
        if not 'channel_name' in kwargs:
            self.channel_name = kwargs['bot_username']
        else:
            self.channel_name = kwargs['channel_name']

class Message:
    def __init__(self, **kwargs) -> None:
        self.content = kwargs['message_content']
        self.sender = kwargs['message_sender']
        self.command = kwargs['message_command']
        self.args = kwargs['message_args']
