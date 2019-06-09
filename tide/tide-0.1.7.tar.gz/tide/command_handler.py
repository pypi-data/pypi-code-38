import traceback
from singleton import singleton
from config import Config
from config_command import ConfigCommand
from config_command_item import ConfigCommandItem
from command_process import CommandProcess
from command_output import CommandOutput
from logging_decorator import logging

@singleton
@logging
class CommandHandler:

    def __init__(self):
        self._child = None
        self._command_process = CommandProcess()

    def spawn_process(self, startup_commands):
        try:
            self._command_process.spawn_process(startup_commands)
            self.__get_output_and_handle_filtering()
        except Exception as ex:
            print("error in command_handler.spawn_child_process(): " + str(ex) + "\n" + traceback.format_exc())

    def run_command(self, command, buffer_name=''):
        try:
            self.__run_event_commands("before_command", command, buffer_name)
            self._command_process.send_command_to_process(command)
            lines = self.__get_output_and_handle_filtering(buffer_name)
            self.__run_event_commands("after_command", command, buffer_name, lines)
            return lines
        except Exception as ex:
            print("error in CommandHandler.run_command(): " + str(ex) + "\n" + traceback.format_exc())

    def close_command_handler(self):
        self._command_process.close_command_process()

    def __run_event_commands(self, event_name, process_command, buffer_name, lines=[]):
        for command in Config().get()["events"].get(event_name) or []:
            cci = ConfigCommandItem()
            cci.command = command
            cci.buffer_name = buffer_name
            cci.args_dict = {'process_command': process_command, 'lines': lines, 'event_name': event_name}
            ConfigCommand().run_config_command(cci)

    def __get_output_and_handle_filtering(self, buffer_name=''):
        output_string = self._command_process.seek_to_end_of_tty()
        return CommandOutput().handle_output_filtering(buffer_name, output_string)
