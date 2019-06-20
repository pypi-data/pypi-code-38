import re
from config import Config
from command_handler import CommandHandler
from action_base import action_base

class run_command_with_match(action_base):

    _command_item = {}
    _buffer_name = ''
    _command_item_command = ''
    _regex_match = ''
    _lines = []
    _match_result = ''
    _try_set_var = ''
    _try_set_array_var = ''
    _else_set = ''

    def run(self, command_item, buffer_name=''):
        self.__set_locals(command_item, buffer_name)
        self._lines = CommandHandler().run_command(self._command_item_command)
        if self._try_set_var:
            self.__get_match()
        if self._try_set_array_var:
            self.__get_array_match()
        self.__try_set_variable()

    def __try_set_variable(self):
        if self._match_result:
            if self._try_set_var:
                Config().get()["variables"][self._try_set_var] = self._match_result
            if self._try_set_array_var:
                Config().get()["variables"][self._try_set_array_var] = self._match_result

    def __set_locals(self, command_item, buffer_name):
        self._command_item = command_item
        self._buffer_name = buffer_name
        self._command_item_command = self._command_item["command"]
        self._regex_match = self._command_item["match"]
        self._try_set_var = command_item.get("try_set", '')
        self._else_set = command_item.get("else_set", '')
        self._try_set_array_var = command_item.get("try_set_array", '')
        if self._try_set_var and self._try_set_array_var:
            raise RuntimeError("error: both try_set and try_set_array have been set. please only set one.")
        self._match_group = command_item.get("match_group", 0)

    def __get_match(self):
        match_string = ''
        for line in (self._lines or []):
            if re.search(self._regex_match, line):
                match = re.search(self._regex_match, line)
                match_string = match.group(int(self._match_group))
        self._match_result = match_string
        if not self._match_result:
            self._match_result = self._else_set

    def __get_array_match(self):
        match_array = []
        for line in (self._lines or []):
            if re.search(self._regex_match, line):
                match = re.search(self._regex_match, line)
                match_array.append(match.group(int(self._match_group)))
        self._match_result = match_array
