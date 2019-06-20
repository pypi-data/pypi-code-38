import shutil
import traceback
import pexpect
from config import Config
from logging_decorator import logging

@logging
class CommandProcess:

    def __init__(self):
        self._child = None
        self._process_path = ''
        self._config_settings = Config().get()["settings"]
        self.__set_process_path()

    def spawn_process(self, startup_commands):
        try:
            self._child = pexpect.spawnu(
                self._process_path +
                self._config_settings["process"]["main_process_default_arguments"] + " " +
                startup_commands)
            self._child.expect(self._config_settings["process"]["end_of_output_regex"])
        except Exception as ex:
            print("error in command_handler.spawn_child_process(): " + str(ex) + "\n" + traceback.format_exc())

    def close_command_process(self):
        del self._child

    def send_command_to_process(self, command):
        self._child.sendline(command)
        self._child.expect(self._config_settings["process"]["end_of_output_regex"])

    def __set_process_path(self):
        if self._config_settings["process"]["find_full_process_name"]:
            self._process_path = shutil.which(self._config_settings["process"]["main_process_name"])
        else:
            self._process_path = self._config_settings["process"]["main_process_name"]
        if not self._process_path:
            raise RuntimeError("error: unable to specify a process name for pexpect")

    def seek_to_end_of_tty(self, timeout=None):
        if not timeout:
            timeout = self._config_settings["process"]["ttl_stream_timeout"]
        output_string = self._child.before
        try:
            while not self._child.expect(r'.+', timeout=timeout):
                output_string += self._child.match.group(0)
        except:
            pass
        return output_string
