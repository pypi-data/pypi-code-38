from config import Config
from command_action import CommandAction
from logging_decorator import logging

@logging
class ConfigCommandItem(object):

    _command = ''
    _event_input_args = {}
    _base_command = ''
    _buffer_name = ''
    _event_input_args_name = ''
    _args_dict = {}
    _user_command_args = []

    @property
    def base_command(self):
        return self._base_command

    @property
    def user_command_args(self):
        return self._user_command_args

    @property
    def buffer_name(self):
        return self._buffer_name

    @buffer_name.setter
    def buffer_name(self, value):
        self._buffer_name = value

    @property
    def event_input_args(self):
        return self._event_input_args

    @event_input_args.setter
    def event_input_args(self, value):
        self._event_input_args = value

    @property
    def event_input_args_name(self):
        return self._event_input_args_name

    @event_input_args_name.setter
    def event_input_args_name(self, value):
        self._event_input_args_name = value

    @property
    def args_dict(self):
        return self._args_dict

    @args_dict.setter
    def args_dict(self, value):
        self._args_dict = value

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        split_command = value.split(' ')
        if len(split_command) > 1:
            self._base_command = split_command[0]
            self._user_command_args = split_command[1:]
        else:
            self._base_command = value
        self.__validate_command()
        self.__set_config_for_user_command_args()

    @property
    def command_action_list(self):
        cal = list(Config().get()["commands"][self.base_command]["steps"])
        ucal = []
        for command_action in cal:
            updated_command_action = command_action.copy()
            event_input_args = self.__get_event_input_args()
            if event_input_args:
                self.event_input_args = event_input_args
                updated_command_action["event_input_args"] = event_input_args
            ucal.append(CommandAction(updated_command_action, self._buffer_name, self._args_dict))
        return ucal

    def __get_event_input_args(self):
        if self._base_command and self.buffer_name and self.event_input_args_name:
           args_dict = {}
           event_command_list = Config().get()["buffers"][self.buffer_name]["events"][self.event_input_args_name]
           for event_command in event_command_list:
               if event_command["command"] == self.base_command:
                   return event_command.get("input_args", [])

    def __set_config_for_user_command_args(self):
        if len(self._user_command_args) > 0:
            Config().get()["variables"]["user_input_args"] = " ".join(self._user_command_args)

    def __validate_command(self):
        commands_list = Config().get()["commands"].keys()
        if not self._base_command in commands_list:
            raise RuntimeError("error: command " + self._base_command + " does not exist in config")
