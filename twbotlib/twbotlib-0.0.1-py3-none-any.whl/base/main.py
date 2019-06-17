from __future__ import annotations
from .struct import Auth, Message
import socket, inspect

class Bot:
    def __init__(self, __auth:Auth, prefix:str='!') -> None:
        self.auth = __auth
        self.sock = socket.socket(socket.SOCK_DGRAM)
        self.__struct_end = '\r\n'
        self.buffer = 1024
        self.logs = False
        self.commands = {}
        self.is_running = False
        self.prefix = prefix
    
    def connect(self) -> bool:
        try:
            self.sock.connect(('irc.twitch.tv', 6667))
            self.sock.send(f'PASS {self.auth.oauth_token}{self.__struct_end}'.encode('utf-8'))
            self.sock.send(f'NICK {self.auth.bot_username}{self.__struct_end}'.encode('utf-8'))
            self.sock.send(f'JOIN #{self.auth.channel_name}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False
    
    def wait_until_join(self) -> None:
        not_completed = True

        while not_completed:
            data = self.sock.recv(self.buffer).decode('utf-8').split('\n')

            for line in data:
                if 'End of /NAMES list' in line:
                    not_completed = False
                if self.logs:
                    print(line)

    def send(self, message:str) -> bool:
        try:
            self.sock.send(f'PRIVMSG #{self.auth.channel_name} :{message}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False

    def read_commands(self, __globals:dict) -> None:
        for command in [x for x in __globals if '__command_' in x]:
            self.commands[command.replace('__command_', '')] = __globals[command]
    
    def run(self) -> None:
        self.is_running = True

        while self.is_running:
            data = self.sock.recv(self.buffer).decode('utf-8').split('\n')

            for line in data:
                if 'PRIVMSG' in line:
                    message = self.getMessageObjectFromStr(line)
                    if self.checkPrefix(message.content) and message.command in self.commands:
                        if len(inspect.signature(self.commands[message.command]).parameters) > 1:
                            self.commands[message.command](message, message.args)
                        else:
                            self.commands[message.command](message)
                if self.logs:
                    print(line)
    
    def checkPrefix(self, __message:str) -> bool:
        return __message[:len(self.prefix)] == self.prefix
    
    def cutMessage(self, __message:str) -> str:
        return __message[len(self.prefix):]

    def getMessageObjectFromStr(self, __string:str) -> Message:
        __string = __string.split('PRIVMSG #')[1]
        try:
            args = self.cutMessage(__string.split(' :')[1]).split(' ', 1)[1].replace('\r', '')
        except:
            args = None
        return Message(
            message_sender=__string.split(' :')[0],
            message_content=__string.split(' :')[1],
            message_command=self.cutMessage(__string.split(' :')[1]).split(' ', 1)[0].replace('\r', '').lower(),
            message_args=args
        )
