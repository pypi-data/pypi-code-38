from __future__ import annotations
from .exceptions import *

def set_bot(bot):
    globals().update(gbot=bot)

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
    
    def __repr__(self) -> str:
        """ The class repr. """

        return f'< Auth({self.bot_username}, {self.oauth_token}) >'

class Message:
    def __init__(self, **kwargs) -> None:
        self.content = kwargs['message_content']
        self.sender = kwargs['message_sender']
        self.command = kwargs['message_command']
        self.channel = Channel(kwargs['message_channel'])
        self.args = kwargs['message_args']
    
    def __repr__(self) -> str:
        """ The class repr. """
        
        return f'<Message(#{self.channel}, @{self.sender})>'

class Channel:
    def __init__(self, channel_name) -> None:
        self.name = channel_name
    
    async def send(self, message:str) -> None:
        await gbot.send(message, self.name)
    
    def __repr(self) -> str:
        """ The class repr. """
        
        return f'<Channel(#{self.name})>'
