import os
import threading
from copy import deepcopy
from .console import curses


class Config:
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    os_name = ''
    settings = {}
    settings_path = ''
    no_bold = False
    space_char = "_"
    backup_settings = {}
    colors = {}
    debug = os.environ.get('DEBUG', 0)
    bold_text = curses.A_BOLD

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = super().__new__(cls)
        return cls.__singleton_instance

    def __init__(self, app):
        self.app = app
        self._init_system_settings()
        self.set_default_settings()
        if not self.load_settings():
            self.save_settings()

    def _init_system_settings(self):
        self.os_name = self.get_os_name()
        user_path = os.path.expanduser('~')
        if self.os_name == 'Macintosh':
            self.settings_path = user_path + '/Library/Preferences/lexed'
        else:
            self.settings_path = user_path + '/.lexed'

    @staticmethod
    def get_os_name():
        system_info = os.uname()
        if 'Linux' in system_info:
            operating_system = 'Linux'
        elif 'Darwin' in system_info or 'Macintosh' in system_info:
            operating_system = 'Macintosh'
        else:
            operating_system = 'Other'
        return operating_system

    def set_default_settings(self, colors_only=False, skip_mono=False):
        settings = {}
        if not skip_mono:
            if self.no_bold:
                self.bold_text = 0
            else:
                self.bold_text = curses.A_BOLD
            settings['mono_normal'] = 0
            settings['mono_reverse'] = curses.A_REVERSE
            settings['mono_bold'] = self.bold_text
            settings['mono_underline'] = curses.A_UNDERLINE
            settings['mono_reverse_bold'] = curses.A_REVERSE + self.bold_text
            settings['mono_reverse_underline'] = curses.A_REVERSE + curses.A_UNDERLINE

        settings.update({key: settings[value] for key, value in {
            'color_normal': 'mono_normal',
            'color_background': 'mono_normal',
            'color_dim': 'mono_normal',
            'color_number': 'mono_normal',
            'color_warning': 'mono_reverse_bold',
            'color_message': 'mono_reverse',
            'color_reversed': 'mono_reverse',
            'color_underline': 'mono_underline',
            'color_commands': 'mono_underline',
            'color_quote_single': 'mono_bold',
            'color_quote_double': 'mono_bold',
            'color_quote_triple': 'mono_bold',
            'color_line_numbers': 'mono_normal',
            'color_line_num_reversed': 'mono_reverse',
            'color_operator': 'mono_normal',
            'color_entry': 'mono_reverse',
            'color_functions': 'mono_underline',
            'color_functions_reversed': 'mono_reverse',
            'color_commands_reversed': 'mono_reverse',
            'color_mark': 'mono_reverse_underline',
            'color_entry_command': 'mono_reverse_bold',
            'color_entry_quote': 'mono_reverse',
            'color_entry_quote_triple': 'mono_reverse',
            'color_entry_comment': 'mono_reverse',
            'color_entry_functions': 'mono_reverse_bold',
            'color_entry_class': 'mono_reverse_bold',
            'color_entry_dim': 'mono_reverse',
            'color_entry_number': 'mono_reverse',
            'color_comment': 'mono_normal',
            'color_comment_block': 'mono_reverse',
            'color_comment_separator': 'mono_reverse',
            'color_comment_leftjust': 'mono_reverse',
            'color_comment_rightjust': 'mono_reverse',
            'color_comment_centered': 'mono_reverse',
            'color_tab_odd': 'mono_normal',
            'color_tab_even': 'mono_bold',
            'color_whitespace': 'mono_reverse_underline',
            'color_class': 'mono_underline',
            'color_class_reversed': 'mono_reverse',
            'color_negative': 'mono_normal',
            'color_entry_negative': 'mono_reverse',
            'color_positive': 'mono_normal',
            'color_entry_positive': 'mono_reverse',
            'color_header': 'mono_normal',
            'color_bar': 'mono_normal',
            'color_constant': 'mono_normal',
            'color_entry_constant': 'mono_reverse',
            'color_selection': 'mono_reverse_underline',
            'color_selection_reversed': 'mono_underline',
        }.items()})
        if not colors_only:
            settings['entry_highlighting'] = True
            settings['syntax_highlighting'] = True
            settings['live_syntax'] = True
            settings['debug'] = True
            settings['collapse_functions'] = False
            settings['splitscreen'] = False
            settings['showSpaces'] = False
            settings['show_indent'] = True
            settings['inline_commands'] = True  # set to 'protected' to protect commands with protect string
            settings['protect_string'] = '::'
            settings['format_comments'] = True
            settings['display_color'] = True
            settings['default_colors'] = True
            settings['auto'] = False
            settings['page_guide'] = False
            settings['cursor_acceleration'] = True
            # The following settings can only be changed by manually editing pref file
            settings['cursor_max_horizontal_speed'] = 5
            settings['cursor_max_vertical_speed'] = 12
            settings['encrypt_warning'] = True
            settings['skip_confirmation'] = False
            settings['highlight_commands'] = True
            settings['deselect_on_copy'] = False
            settings['select_on_paste'] = False
            # settings['default_load_sort'] = 'name'
            # settings['default_load_reverse'] = False
            # settings['default_load_invisibles'] = False
            settings['key_entry_window'] = 5
            settings['key_find'] = 6
            settings['key_find_again'] = 7
            settings['key_next_bug'] = 4
            settings['key_next_marked'] = 14
            settings['key_previous_marked'] = 2
            settings['key_deselect_all'] = 1
            settings['key_page_down'] = 16
            settings['key_page_up'] = 21
            settings['key_save_as'] = 23
            settings['terminal_command'] = 'gnome-terminal -x'  # to launch in xterm, set to 'xterm -e'

        settings['default_load_sort'] = 'name'  # Had to define these here to fix bug
        settings['default_load_reverse'] = False
        settings['default_load_invisibles'] = False

        self.settings = settings

    def load_settings(self):
        result = False
        if os.path.exists(self.settings_path):
            with open(self.settings_path) as config_file:
                for line in config_file:
                    key, value = (x.strip() for x in line.strip().split('='))
                    try:
                        value = int(value)  # convert value to number if possible
                    except (ValueError, TypeError):
                        pass
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                    self.settings[key] = value
            result = True
        return result

    def save_settings(self):
        # global program_message
        editor = getattr(self.app, 'editor', None)
        if editor:
            editor.reset_line()
        settings_list = []
        for key, value in self.settings.items():
            line_of_text = f'{key} = {value}\n'
            settings_list.append(line_of_text)
        settings_list.sort()

        with open(self.settings_path, 'w') as config_file:
            config_file.writelines(settings_list)

        if editor:
            editor.program_message = ' Settings saved '

    def invert_monochrome(self):
        """Inverts monochrome display"""
        self.settings.update({
            'mono_bold': 2359296,
            'mono_normal': 262144,
            'mono_reverse': 0,
            'mono_reverse_bold': 2097152,
            'mono_reverse_underline': 131072,
            'mono_underline': 393216,
        })

    def set(self, key, value):
        self.settings[key] = value

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def __getitem__(self, key, default=None):
        return self.settings.get(key, default)

    def __setitem__(self, key, value):
        self.settings[key] = value

    def copy_settings(self, reverse=False):
        """Makes a backup copy of current settings

                If optional arg reverse is set to 'True',
                settings is copied from backup"""
        # global settings, backupSettings
        if reverse:
            self.settings = deepcopy(self.backup_settings)
        else:
            self.backup_settings = deepcopy(self.settings)
