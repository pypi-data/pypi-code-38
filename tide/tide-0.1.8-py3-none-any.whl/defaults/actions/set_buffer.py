import os
import vim
from action_base import action_base
from config import Config
import interpolate as Interpolate

class set_buffer(action_base):

    _command_item = ''
    _calling_buffer_name = ''
    _buffer_name = ''
    _file_name = ''
    _buffer_filename_variable = ''
    _buffer_filename = ''
    _buffer_window_number = ''

    def run(self, command_item, buffer_name=''):
        self.__set_locals(command_item, buffer_name)
        if self._buffer_filename_variable:
            self.__set_buffer_from_filename()
        else:
            self.__load_buffer_cache_from_file()
            self.__run_vim_command()

    def __try_get_buffer_window_number(self):
        mapped_file_buffers = Config().get()["internal"]["variables"].get("mapped_file_buffers", {})
        if not mapped_file_buffers:
            Config().get()["internal"]["variables"]["mapped_file_buffers"] = {}
        self._buffer_window_number = mapped_file_buffers.get(self._buffer_name, '')

    def __set_buffer_window_mapping(self):
        self._buffer_window_number = vim.eval("vg_buffer_find#find_window_by_bufname('" + self._buffer_name + "', 1)")
        Config().get()["internal"]["variables"]["mapped_file_buffers"][self._buffer_name] = self._buffer_window_number
        vim.command("set buftype=")
        vim.command("set modifiable")

    def __switch_to_window_number_set_active_file(self):
        vim.command(str(self._buffer_window_number) + "wincmd w")
        vim.command("silent edit! " + self._buffer_filename)

    def __set_buffer_from_filename(self):
        self.__try_get_buffer_window_number()
        if not self._buffer_window_number:
            self.__set_buffer_window_mapping()
        self.__switch_to_window_number_set_active_file()

    def __load_buffer_cache_from_file(self):
        if os.path.isfile(self._file_name):
            file_handle = open(self._file_name, 'r+')
            lines = [line.rstrip('\n') for line in file_handle.readlines()]
            file_handle.close()
            Config().get()["internal"]["buffer_caches"][self._buffer_name] = lines
        else:
            raise RuntimeError("error: unable to find file: " + self._file_name)

    def __run_vim_command(self):
        vim_command = "call vg_display#default_display_buffer('" + self._buffer_name + "')"
        vim.command(vim_command)

    def __set_locals(self, command_item, buffer_name):
        self._command_item = command_item
        self._calling_buffer_name = buffer_name
        self._buffer_name = Interpolate.interpolate_variables(self._command_item["buffer_name"])
        self._file_name = Interpolate.interpolate_variables(self._command_item["file_name"])
        self._buffer_filename_variable = Config().get()["buffers"][self._buffer_name].get('buffer_filename_variable', '')
        if self._buffer_filename_variable:
            self._buffer_filename = Config().get()["variables"].get(self._buffer_filename_variable, '')
