from __future__ import annotations
from .struct import *
import socket, inspect, asyncio

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
        self.loop = asyncio.get_event_loop()
        set_bot(self)
    
    def connect(self) -> bool:
        """ Connection to the twitch IRC socket and returning boolean (On success is True and on fail is False). """

        try:
            self.sock.connect(('irc.twitch.tv', 6667))
            self.sock.send(f'PASS {self.auth.oauth_token}{self.__struct_end}'.encode('utf-8'))
            self.sock.send(f'NICK {self.auth.bot_username}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False
    
    async def join(self, channel_name:str=None) -> bool:
        """ Join a channel by channel_name and returning boolean (On success is True and on fail is False). """

        if not channel_name:
            channel_name = self.auth.channel_name
        
        try:
            self.sock.send(f'JOIN #{channel_name}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False
    
    async def depart(self, channel_name:str=None) -> bool:
        """ Depart a channel by channel_name and returning boolean (On success is True and on fail is False). """

        if not channel_name:
            channel_name = self.auth.channel_name
        
        try:
            self.sock.send(f'PART #{channel_name}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False
    
    async def wait_until_join(self) -> None:
        """ Wait until the bot is joined the chat. """

        not_completed = True
        while not_completed:
            data = self.sock.recv(self.buffer).decode('utf-8').split('\n')

            for line in data:
                if 'End of /NAMES list' in line:
                    not_completed = False
                if self.logs:
                    print(line)

    async def send(self, message:str, channel_name:str=None) -> bool:
        """ Send message (string) to the connected chat and returning boolean (On success is True and on fail is False). """

        if not channel_name:
            channel_name = self.auth.channel_name

        try:
            self.sock.send(f'PRIVMSG #{channel_name} :{message}{self.__struct_end}'.encode('utf-8'))
            return True
        except:
            return False

    def read_commands(self, __globals:dict) -> None:
        """ Read the exists commands from the file-globals. """

        for command in [x for x in __globals if '__command_' in x]:
            self.commands[command.replace('__command_', '')] = __globals[command]
    
    def run(self, startup_function=None) -> None:
        """ Run the bot and start the main while. """

        self.loop.create_task(self.mainloop(startup_function))
        self.loop.run_forever()
    
    async def mainloop(self, startup_function) -> None:
        """ The main loop that reads and process the incoming data. """

        if startup_function:
            await startup_function()

        self.is_running = True
        while self.is_running:
            data = self.sock.recv(self.buffer).decode('utf-8').split('\n')

            for line in data:
                if 'PRIVMSG' in line:
                    message = self.getMessageObjectFromStr(line)
                    if self.checkPrefix(message.content) and message.command in self.commands:
                        if len(inspect.signature(self.commands[message.command]).parameters) > 1:
                            await self.commands[message.command](message, message.args)
                        else:
                            await self.commands[message.command](message)
                if self.logs:
                    print(line)
    
    async def change_name_color(self, color:str) -> bool:
        """ Changes the bot name color and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/color {color}')
            return True
        except:
            return False
    
    async def me(self, text:str) -> bool:
        """ Sends a message with the /me command and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/me {text}')
            return True
        except:
            return False
    
    async def enable_slowmode(self, seconds:int=5) -> bool:
        """ Enables slowmode and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/slow {seconds}')
            return True
        except:
            return False
    
    async def disable_slowmode(self) -> bool:
        """ Disables slowmode and returning boolean (On success is True and on fail is False). """

        try:
            await self.send('/slowoff')
            return True
        except:
            return False
    
    async def clearchat(self) -> bool:
        """ Disables slowmode and returning boolean (On success is True and on fail is False). """

        try:
            await self.send('/clear')
            return True
        except:
            return False
    
    async def mod(self, username:str) -> bool:
        """ Gives moderator by username argument and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/mod {username}')
            return True
        except:
            return False
    
    async def unmod(self, username:str) -> bool:
        """ Removes moderator by username argument and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/unmod {username}')
            return True
        except:
            return False
    
    async def vip(self, username:str) -> bool:
        """ Gives vip by username argument and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/vip {username}')
            return True
        except:
            return False
    
    async def unvip(self, username:str) -> bool:
        """ Removes vip by username argument and returning boolean (On success is True and on fail is False). """

        try:
            await self.send(f'/unvip {username}')
            return True
        except:
            return False
    
    def checkPrefix(self, __message:str) -> bool:
        """ Check if message starts with the prefix. """

        return __message[:len(self.prefix)] == self.prefix
    
    def cutMessage(self, __message:str) -> str:
        """ Cutting the prefix from the message. """

        return __message[len(self.prefix):]

    def getMessageObjectFromStr(self, __string:str) -> Message:
        """ Returning Message object from string. """
        
        try:
            args = self.cutMessage(__string.split('PRIVMSG #')[1].split(' :')[1]).split(' ', 1)[1].replace('\r', '')
        except:
            args = None
        return Message(
            message_sender=__string[1:].split('!', 1)[0],
            message_content=__string.split('PRIVMSG #')[1].split(' :')[1],
            message_command=self.cutMessage(__string.split('PRIVMSG #')[1].split(' :')[1]).split(' ', 1)[0].replace('\r', ''),
            message_channel=__string.split('PRIVMSG #')[1].split(' :')[0],
            message_args=self.argparse(args)
        )
    
    def __repr__(self) -> str:
        """ The class repr. """

        return f'<Bot(@{self.auth.bot_username})>'
    
    @staticmethod
    def argparse(args_string:str) -> list:
        in_string, space_cut = False, False
        out, listout = '', []
        for i, c in enumerate(args_string):
            if not in_string:
                if c != '"':
                    if c == ' ' and not space_cut:
                        space_cut = True
                        if out != '':
                            listout.append(out)
                            out = ''
                    elif not space_cut:
                        out += c
                    elif space_cut and c != ' ':
                        space_cut = False
                        out += c
            elif c != '"':
                out += c
            if c == '"':
                in_string = not in_string
        if out:
            listout.append(out)
        return listout
