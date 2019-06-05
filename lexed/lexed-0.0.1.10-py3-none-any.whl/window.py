import os
import threading

from .meta import BareException
from .editor import Editor
from .const import CHAR_DICT, HELP_GUIDE
from .console import curses


class Window:
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = super().__new__(cls)
        return cls.__singleton_instance

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.colors = {}
        self.c = ''

        # Initialize curses window
        self.screen = curses.initscr()

        curses.noecho()  # turns off echoing of keys to the screen
        curses.cbreak()  # read keys without requiring Enter key

        self.screen.keypad(1)  # Enable keypad mode (read special keys)

        self.height, self.width = self.screen.getmaxyx()  # GRABS SIZE of CURRENT TERMINAL WINDOW
        # (self.height, self.width) = windowSize  # split into height and width

        self.height -= 1
        self.width -= 1

        self._win = curses.newwin(self.height, self.width, 0, 0)  # 0,0 is start position
        self.editor = Editor(self)

    def print_header(self, save_info='', message='', save_path='', total=0):
        """Prints header to curses screen"""
        if message:
            # Print info message
            self.screen.addstr(0, 0, (' ' * self.width),
                               self.config['color_header'])  # this was commented out, not sure why
            self.screen.addstr(0, 0, message, self.config['color_message'])
        else:
            self.screen.addstr(0, 0, (' ' * self.width), self.config['color_header'])  # print empty line
            if not save_path:
                self.screen.addstr(0, 0, 'file/not/saved', self.config['color_header'])  # print file/not/saved
            elif len(save_path) > self.width - 14:
                temp_text = os.path.split(save_path)[1]
                self.screen.addstr(0, 0, '%s%s' % (temp_text, save_info),
                                   self.config['color_header'])  # print filename only
            else:
                self.screen.addstr(0, 0, '%s%s' % (save_path, save_info),
                                   self.config['color_header'])  # print directory and filename

        temp_text = '%i' % total
        lines_text = temp_text.rjust(11)
        if self.config['inline_commands'] == 'protected':
            protect_string = str(self.config['protect_string'])
            self.screen.addstr(0, self.width - 12 - len(protect_string) - 1, lines_text, self.config['color_header'])
            self.screen.addstr(0, self.width - len(protect_string) - 1, protect_string, self.config['color_message'])
        else:
            self.screen.addstr(0, self.width - 12, lines_text, self.config['color_header'])

        self.screen.hline(1, 0, curses.ACS_HLINE, self.width, self.config['color_bar'])

    def addstr(self, *args, **kwargs):
        self.screen.addstr(*args, **kwargs)

    def hline(self, *args, **kwargs):
        self.screen.hline(*args, **kwargs)

    def getch(self, *args, **kwargs):
        self.c = self.screen.getch(*args, **kwargs)
        if self.c == 10 and self.config.debug:
            self.screen.nodelay(1)
            while self.screen.getch() >= 0:
                pass
            self.screen.nodelay(0)

        return self.c

    def vline(self, *args, **kwargs):
        self.screen.vline(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        self.screen.refresh(*args, **kwargs)

    def clear(self, *args, **kwargs):
        self.screen.clear(*args, **kwargs)

    def keypad(self, *args, **kwargs):
        self.screen.keypad(*args, **kwargs)

    def status_message(self, text, number, total, update_lines=False):
        """Displays status message"""
        if update_lines:  # clears entire header and updates number of lines
            self.addstr(0, 0, ' ' * self.width, self.config['color_header'])
            temp_text = f'{total:d}'
            lines_text = temp_text.rjust(11)
            if self.config['inline_commands'] == 'protected':
                protect_string = str(self.config['protect_string'])
                self.addstr(0, self.width - 12 - len(protect_string) - 1, lines_text, self.config['color_header'])
                self.addstr(0, self.width - len(protect_string) - 1, protect_string, self.config['color_message'])
            else:
                self.addstr(0, self.width - 12, lines_text, self.config['color_header'])
        else:  # clears space for statusMessage only
            self.addstr(0, 0, " " * (self.width - 13), self.config['color_header'])
        number = int(number)  # Convert to integer
        message = f' {text}{number:d}% '
        self.addstr(0, 0, message, self.config['color_warning'])
        self.refresh()

    def get_confirmation(self, text=' Are you sure? (y/n) ', any_key=False, x=0, y=0):
        """Confirm selection in new (centered) window. Returns 'True' if 'y' pressed."""
        if not any_key and self.config['skip_confirmation'] and text != ' File exists, overwrite? (y/n) ':
            return True
        side = '   '
        if len(text) < 15:
            diff = 15 - len(text)
            spacer = ' ' * int(diff / 2)
            text = spacer + text + spacer
        line = (len(text) + (len(side) * 2)) * ' '

        half_height = int(self.height / 2)
        self.hline(half_height - 1, int(self.width / 2) - int(len(text) / 2) - len(side),
                   curses.ACS_HLINE, (len(text) + 6), self.config["color_message"])
        # print corners
        self.hline(half_height - 1, int(self.width / 2) - int(len(text) / 2) - len(side),
                   curses.ACS_ULCORNER, 1, self.config["color_message"])
        self.hline(half_height - 1, int(self.width / 2) - int(len(text) / 2) + len(text) + 2,
                   curses.ACS_URCORNER, 1, self.config["color_message"])

        self.addstr(half_height + 1, int(self.width / 2) - int(len(text) / 2) - len(side),
                    line, self.config["color_message"])  # Prints blank line
        self.addstr(half_height, int(self.width / 2) - int(len(text) / 2) - len(side),
                    side, self.config["color_message"])  # Prints left side
        self.vline(half_height, int(self.width / 2) - int(len(text) / 2) - len(side),
                   curses.ACS_VLINE, 3, self.config["color_message"])  # prints left side

        self.addstr(half_height, int(self.width / 2) - int(len(text) / 2),
                    text, self.config["color_message"])  # Prints text message

        self.addstr(half_height, int(self.width / 2) - int(len(text) / 2) + len(text),
                    side, self.config["color_message"])  # Prints right side
        self.vline(half_height, int(self.width / 2) - int(len(text) / 2) + len(text) + 2,
                   curses.ACS_VLINE, 3, self.config["color_message"])  # prints right side

        if any_key:
            self.addstr(half_height + 1, int(self.width / 2) - int(len("(press any key)") / 2),
                        "(press any key)", self.config["color_message"])
        self.hline(half_height + 2, int(self.width / 2) - int(len(text) / 2) - len(side),
                   curses.ACS_HLINE, (len(text) + 6), self.config["color_message"])
        # print bottom corners
        self.hline(half_height + 2, int(self.width / 2) - int(len(text) / 2) - len(side),
                   curses.ACS_LLCORNER, 1, self.config["color_message"])
        self.hline(half_height + 2, int(self.width / 2) - int(len(text) / 2) + len(text) + 2,
                   curses.ACS_LRCORNER, 1, self.config["color_message"])

        # Prints text message
        try:
            self.addstr(y + self.height - 2, x, "",
                        self.config["color_normal"])  # Moves cursor to previous position
        except BareException:
            pass

        self.refresh()
        self.c = ''
        while True:
            self.c = self.getch()
            if any_key and self.c:
                return True
            if self.c == ord('y') or self.c == ord('Y'):
                pos = text.find("y")
                self.addstr(half_height, (int(self.width / 2) - int(len(text) / 2) + pos), 'y',
                            self.config["color_quote_double"])  # Prints text message
                self.refresh()
                return True
            if self.c == ord('n') or self.c == ord('N'):
                return False

    def prompt_user(self, title='ENTER COMMAND:', default_answer='',
                    footer="(press 'enter' to proceed, UP arrow to cancel)", adjust_pos=False):
        """
        Displays window and prompts user to enter command
        Used for 'Entry', 'Find', and 'Save' windows
        """

        self.c = ''
        if adjust_pos and '.' in default_answer and default_answer.rfind('.') == len(default_answer) - 4:
            position = len(default_answer) - 4
        elif adjust_pos and '.' in default_answer and default_answer.rfind('.') == len(default_answer) - 3:
            position = len(default_answer) - 3
        else:
            position = len(default_answer)
        text = default_answer
        # side = '   '
        line = int(self.width - 16) * ' '
        if self.width < 70 and footer == "(press 'enter' to proceed, UP arrow to cancel)":
            footer = '(press UP arrow to cancel)'
        footer = footer.center(int(self.width - 16) - 6)
        empty_line = (int(self.width - 16) - 6) * ' '
        if len(text) > len(empty_line) * 2:
            text = text[0:(len(empty_line) * 2)]

        half_height = int(self.height / 2)
        while self.c != 10:
            for i in range(0, 6):
                self.addstr(half_height - 2 + i, 8, line, self.config['color_message'])
            self.addstr(half_height - 1, 11, title, self.config['color_message'])
            self.addstr(half_height + 2, 11, footer, self.config['color_message'])
            self.addstr(half_height, 11, empty_line, self.config['color_normal'])
            self.addstr(half_height + 1, 11, empty_line, self.config['color_normal'])

            # print border
            self.hline(half_height - 2, 9, curses.ACS_HLINE, (len(empty_line) + 4), self.config['color_message'])
            self.hline(half_height + 3, 9, curses.ACS_HLINE, (len(empty_line) + 4), self.config['color_message'])
            self.vline(half_height - 2, 8, curses.ACS_VLINE, 6, self.config['color_message'])
            self.vline(half_height - 2, (len(empty_line) + 13), curses.ACS_VLINE, 6, self.config['color_message'])
            self.hline(half_height - 2, 8, curses.ACS_ULCORNER, 1, self.config['color_message'])
            self.hline(half_height + 3, 8, curses.ACS_LLCORNER, 1, self.config['color_message'])
            self.hline(half_height - 2, (len(empty_line) + 13), curses.ACS_URCORNER, 1, self.config['color_message'])
            self.hline(half_height + 3, (len(empty_line) + 13), curses.ACS_LRCORNER, 1, self.config['color_message'])

            if len(text) > len(empty_line):
                self.addstr(half_height, 11, text[0:len(empty_line)], self.config['color_normal'])
                self.addstr(half_height + 1, 11, text[len(empty_line):], self.config['color_normal'])
            else:
                self.addstr(half_height, 11, text, self.config['color_normal'])

                if len(text) == len(empty_line) and position == len(empty_line):
                    self.addstr(half_height + 1, 11, '', self.config['color_normal'])  # Moves cursor to second line

            # Move cursor
            if position < len(empty_line):
                self.addstr(half_height, position + 11, '', self.config['color_normal'])
            else:
                self.addstr(half_height + 1, position + 11 - len(empty_line), '', self.config['color_normal'])

            self.refresh()
            c = self.getch()

            part1 = text[0:position]
            part2 = text[position:]

            if c in (curses.KEY_UP, self.config['key_find'],
                     self.config['key_entry_window'], self.config['key_save_as']):
                return False
            if c == curses.KEY_LEFT:
                position -= 1
            if c == curses.KEY_RIGHT:
                position += 1
            position = max(0, min(position, len(text)))

            if c == curses.KEY_BACKSPACE or c == 127:
                try:
                    text = part1[0:-1] + part2
                except BareException:
                    pass
                position -= 1

            elif c in CHAR_DICT:
                text = (part1 + CHAR_DICT[c] + part2)
                position += 1
        # attempt to hide encrypt password during load/save
        self.addstr(half_height, 11, empty_line, self.config['color_normal'])
        self.addstr(half_height + 1, 11, empty_line, self.config['color_normal'])
        self.refresh()

        return text

    def print_background(self):
        """Displays background color"""
        for i in range(0, self.height + 2):
            try:
                self.addstr(i, 0, (' ' * self.width), self.config['color_background'])
            except BareException:
                return

    def draw_line_number_background(self):
        """Draws background for line numbers"""
        for y in range(2, self.height + 1):
            self.addstr(y, 0, '     ', self.config['color_line_numbers'])  # Prints blank line number block

    def draw_page_guide(self, end_pos=0):  # , hline_pos=1):
        """Draws page guide"""
        end_pos = end_pos or self.height + 1
        if self.width <= (self.config['page_guide'] + 6):
            return

        for i in range(2, end_pos):
            self.vline(i, (self.config['page_guide'] + 6), curses.ACS_VLINE, 1,
                       self.config['color_bar'])  # prints vertical line
        self.hline(1, (self.config['page_guide'] + 6), curses.ACS_TTEE, 1, self.config['color_bar'])

    def color_on(self, default_colors=False):
        """Turn on curses color and handle color assignments"""
        # global program_message
        self.editor.reset_line()

        if curses.has_colors():
            curses.start_color()
        else:
            if self.config.os_name == 'Macintosh':
                self.editor.get_confirmation('Color not supported on the OSX terminal!', True)
            else:
                self.editor.get_confirmation('Color not supported on your terminal!', True)
            self.config.set_default_settings(True, True)
            self.config['display_color'] = False
            self.editor.program_message = ' Monochrome display '
            return

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_MAGENTA)

        curses.init_pair(15, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(16, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(17, curses.COLOR_RED, curses.COLOR_WHITE)

        curses.init_pair(18, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(19, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(20, curses.COLOR_WHITE, curses.COLOR_RED)

        curses.init_pair(21, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(22, curses.COLOR_BLUE, curses.COLOR_RED)

        curses.init_pair(23, curses.COLOR_MAGENTA, curses.COLOR_GREEN)
        curses.init_pair(24, curses.COLOR_GREEN, curses.COLOR_MAGENTA)

        curses.init_pair(25, curses.COLOR_YELLOW, curses.COLOR_GREEN)
        curses.init_pair(26, curses.COLOR_GREEN, curses.COLOR_YELLOW)

        curses.init_pair(27, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(28, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(29, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(30, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(31, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        curses.init_pair(32, curses.COLOR_CYAN, curses.COLOR_BLUE)

        curses.init_pair(33, curses.COLOR_CYAN, curses.COLOR_WHITE)
        curses.init_pair(34, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        curses.init_pair(35, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        curses.init_pair(36, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(37, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(38, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(39, curses.COLOR_GREEN, curses.COLOR_RED)
        curses.init_pair(40, curses.COLOR_YELLOW, curses.COLOR_RED)
        curses.init_pair(41, curses.COLOR_CYAN, curses.COLOR_RED)
        curses.init_pair(42, curses.COLOR_MAGENTA, curses.COLOR_RED)
        curses.init_pair(43, curses.COLOR_BLUE, curses.COLOR_GREEN)
        curses.init_pair(44, curses.COLOR_CYAN, curses.COLOR_GREEN)
        curses.init_pair(45, curses.COLOR_RED, curses.COLOR_GREEN)
        curses.init_pair(46, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(47, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(48, curses.COLOR_BLUE, curses.COLOR_CYAN)
        curses.init_pair(49, curses.COLOR_RED, curses.COLOR_CYAN)
        curses.init_pair(50, curses.COLOR_YELLOW, curses.COLOR_CYAN)
        curses.init_pair(51, curses.COLOR_MAGENTA, curses.COLOR_CYAN)

        curses.init_pair(52, curses.COLOR_BLUE, curses.COLOR_YELLOW)

        self.colors.update({
            "white_on_black": curses.color_pair(1),
            "cyan_on_black": curses.color_pair(2),
            "blue_on_black": curses.color_pair(3),
            "green_on_black": curses.color_pair(4),
            "yellow_on_black": curses.color_pair(5),
            "red_on_black": curses.color_pair(6),
            "magenta_on_black": curses.color_pair(7),

            "black_on_white": curses.color_pair(8),
            "black_on_cyan": curses.color_pair(9),
            "black_on_blue": curses.color_pair(10),
            "black_on_green": curses.color_pair(11),
            "black_on_yellow": curses.color_pair(12),
            "black_on_red": curses.color_pair(13),
            "black_on_magenta": curses.color_pair(14),

            "blue_on_white": curses.color_pair(15),
            "green_on_white": curses.color_pair(16),
            "red_on_white": curses.color_pair(17),

            "white_on_blue": curses.color_pair(18),
            "white_on_green": curses.color_pair(19),
            "white_on_red": curses.color_pair(20),

            "red_on_blue": curses.color_pair(21),
            "blue_on_red": curses.color_pair(22),

            "magenta_on_green": curses.color_pair(23),
            "green_on_magenta": curses.color_pair(24),

            "yellow_on_green": curses.color_pair(25),
            "green_on_yellow": curses.color_pair(26),

            "white_on_yellow": curses.color_pair(27),
            "white_on_magenta": curses.color_pair(28),

            "yellow_on_blue": curses.color_pair(29),
            "green_on_blue": curses.color_pair(30),
            "magenta_on_blue": curses.color_pair(31),
            "cyan_on_blue": curses.color_pair(32),

            "cyan_on_white": curses.color_pair(33),
            "yellow_on_white": curses.color_pair(34),
            "magenta_on_white": curses.color_pair(35),
            "white_on_white": curses.color_pair(36),
            "yellow_on_yellow": curses.color_pair(37),
            "black_on_black": curses.color_pair(38),
            "green_on_red": curses.color_pair(39),
            "yellow_on_red": curses.color_pair(40),
            "cyan_on_red": curses.color_pair(41),
            "magenta_on_red": curses.color_pair(42),
            "blue_on_green": curses.color_pair(43),
            "cyan_on_green": curses.color_pair(44),
            "red_on_green": curses.color_pair(45),
            "red_on_yellow": curses.color_pair(46),
            "white_on_cyan": curses.color_pair(47),
            "blue_on_cyan": curses.color_pair(48),
            "red_on_cyan": curses.color_pair(49),
            "yellow_on_cyan": curses.color_pair(50),
            "magenta_on_cyan": curses.color_pair(51),

            "blue_on_yellow": curses.color_pair(52),
        })

        if self.config.no_bold:
            bold = 0
        else:
            bold = curses.A_BOLD
        underline = curses.A_UNDERLINE

        # default colors

        if default_colors or self.config["default_colors"]:
            self.config.settings.update({
                "color_dim": self.colors["white_on_black"],
                "color_line_numbers": self.colors["black_on_yellow"],
                "color_line_num_reversed": self.colors["white_on_blue"] + bold,
                "color_warning": self.colors["white_on_red"] + bold,
                "color_normal": self.colors["white_on_black"] + bold,
                "color_background": self.colors["white_on_black"] + bold,
                "color_message": self.colors["white_on_magenta"] + bold,
                "color_reversed": self.colors["white_on_magenta"] + bold,
                "color_underline": self.colors["white_on_black"] + underline + bold,
                "color_commands": self.colors["green_on_black"] + bold,
                "color_commands_reversed": self.colors["white_on_green"] + bold,
                "color_quote_double": self.colors["yellow_on_black"] + bold,
                "color_comment": self.colors["yellow_on_black"],
                "color_comment_block": self.colors["black_on_yellow"],
                "color_comment_separator": self.colors["black_on_red"],
                "color_comment_leftjust": self.colors["white_on_magenta"] + bold,
                "color_comment_rightjust": self.colors["white_on_red"] + bold,
                "color_comment_centered": self.colors["yellow_on_green"] + bold,
                "color_number": self.colors["cyan_on_black"],
                "color_entry": self.colors["white_on_blue"] + bold,

                "color_entry_command": self.colors["green_on_blue"] + bold,
                "color_entry_quote": self.colors["yellow_on_blue"] + bold,
                "color_entry_quote_triple": self.colors["red_on_blue"] + bold,
                "color_entry_comment": self.colors["red_on_blue"] + bold,
                "color_entry_functions": self.colors["magenta_on_blue"] + bold,
                "color_entry_class": self.colors["cyan_on_blue"] + bold,
                "color_entry_number": self.colors["cyan_on_blue"] + bold,
                "color_entry_dim": self.colors["white_on_blue"],

                "color_operator": self.colors["white_on_black"],
                "color_functions": self.colors["magenta_on_black"] + bold,
                "color_functions_reversed": self.colors["white_on_magenta"] + bold,
                "color_class": self.colors["blue_on_black"] + bold,
                "color_class_reversed": self.colors["white_on_blue"] + bold,
                "color_quote_triple": self.colors["red_on_black"],
                "color_mark": self.colors["yellow_on_blue"] + bold + underline,
                "color_negative": self.colors["red_on_black"] + bold,
                "color_entry_negative": self.colors["red_on_blue"] + bold,
                "color_positive": self.colors["cyan_on_black"] + bold,
                "color_entry_positive": self.colors["cyan_on_blue"] + bold,
                "color_tab_odd": self.colors["white_on_black"],
                "color_tab_even": self.colors["yellow_on_black"],
                "color_whitespace": self.colors["black_on_white"] + underline,
                "color_header": self.colors["white_on_black"] + bold,
                "color_bar": self.colors["white_on_black"],
                "color_constant": self.colors["white_on_black"] + underline,
                "color_entry_constant": self.colors["white_on_blue"] + bold,
                "color_quote_single": self.colors["yellow_on_black"] + bold,
                "color_selection": self.colors["black_on_white"] + underline,
                "color_selection_reversed": self.colors["black_on_cyan"] + underline,
            })
        self.config["display_color"] = True

    def curses_off(self):
        """Turns off curses and resets terminal to normal"""
        curses.nocbreak()
        self.keypad(0)
        curses.echo()  # to turn off curses settings
        curses.endwin()  # restore terminal to original condition

    def print_formatted_text(self, y, string, _type='', width=79):
        """Formats curses text by looking for 'special' characters.

            Type can be "rjust" for right justification, "center" for centered.
            Width should be passed when using Type.

            Text formatting
            ---------------
            '_' = UNDERLINE
            '^' = BOLD
            '*' = REVERSE

            String Replacement
            ------------------
            '$' = DIAMOND
            '|" = Vertical Line"""

        underline = False
        bold = False
        reverse = False
        temp_string = string.replace('*', '')  # REVERSE
        temp_string = temp_string.replace('_', '')  # UNDERLINE
        temp_string = temp_string.replace('^', '')  # BOLD

        if _type == 'rjust':
            x = width - len(temp_string)
        elif _type == 'center':
            x = int((width - len(temp_string)) / 2)
        else:
            x = 0

        for z in range(0, len(string)):  # easy way to make first letter of each word standout
            item = string[z]
            if item == '_':
                underline = True
            elif item == '^':
                bold = True
            elif item == '*':
                reverse = True
            elif item == '$':
                self.hline(y, x, curses.ACS_DIAMOND, 1, self.config['color_normal'])  # print diamond
                x += 1
            elif item == '|' and reverse:
                self.vline(y, x, curses.ACS_VLINE, 1, self.config['color_reversed'])  # prints vertical line
                reverse = False
                x += 1
            elif item == '|' and bold:
                self.vline(y, x, curses.ACS_VLINE, 1, self.config.bold_text)  # prints vertical line
                reverse = False
                x += 1
            elif item == '|':
                self.vline(y, x, curses.ACS_VLINE, 1, self.config['color_bar'])  # prints vertical line
                self.hline(y - 1, x, curses.ACS_TTEE, 1, self.config['color_bar'])  # Format previous line
                underline = False
                x += 1
            elif underline:
                underline = False
                self.addstr(y, x, item, self.config['color_underline'])
                x += 1
            elif bold:
                self.addstr(y, x, item, self.config.bold_text)
                bold = False
                x += 1
            elif reverse:
                self.addstr(y, x, item, self.config['color_reversed'])
                reverse = False
                x += 1
            else:
                self.addstr(y, x, item, self.config['color_header'])
                x += 1

    def set_colors(self):
        """Function that allows user to set colors used with syntax highlighting"""
        # global program_message
        self.editor.reset_line()
        if not self.config['display_color'] or not curses.has_colors():
            self.editor.get_confirmation("You can't set colors in monochrome mode!", True)
            return
        if self.width < 79 or self.height < 19:
            self.editor.get_confirmation('Increase terminal size to set colors!', True)
            return

        self.config['default_colors'] = False
        # win = \
        curses.newwin(self.height, self.width, 0, 0)  # 0,0 is start position
        x = int((self.width - 49) / 2)
        c = 0
        i_num = 0
        item_list = []
        c_num = 0
        color_list = []
        temp_list = []
        empty = ''.center(49)
        separator = ''.center(49, '@')
        style = 0
        # style_change = False

        for key in self.config.settings.keys():
            if 'color_' in key:
                item_list.append(key)
        for key in self.colors.keys():
            (item1, item2) = key.split('_on_')
            temp_list.append((item2 + item1, key))  # change "white_on_blue" to ("bluewhite", "white_on_blue")
        temp_list.sort()

        for value in temp_list:
            color_list.append(value[1])

        item_list.sort()
        color_list.insert(0, '[CURRENT]')

        for i in range(0, self.height + 1):
            self.addstr(i, 0, (' ' * self.width), self.config['color_normal'])
            if i <= 8:
                self.addstr(i, x, empty, curses.A_NORMAL)  # redundant?
        title = 'SETCOLORS'.center(49)
        header = ' ITEM (up/down)               COLOR (left/right)'
        # divider = "".center(49, '-')
        # footer = '*N*o*r*m*a*l $ _Bold $ _Underline $ b_Oth'

        sample_header = 'SAMPLE LAYOUT'.center(49)
        sample_left = 'Left justified'.ljust(49)
        sample_right = 'Right justified'.rjust(49)

        while c != 10:  # continue until 'enter' is pressed
            item = item_list[i_num]
            color = color_list[c_num]
            self.addstr(1, x, title, curses.A_REVERSE)
            self.addstr(2, x, header, curses.A_BOLD)
            self.hline(3, x, curses.ACS_HLINE, 49, self.config['color_bar'])
            if color == '[CURRENT]':
                search = ''
                for key, value in self.colors.items():
                    if self.config[item] == value:
                        search = key
                        style = 0
                    elif self.config[item] == value + curses.A_BOLD:
                        search = key
                        style = curses.A_BOLD
                    elif self.config[item] == value + curses.A_UNDERLINE:
                        search = key
                        style = curses.A_UNDERLINE
                    elif self.config[item] == value + curses.A_BOLD + curses.A_UNDERLINE:
                        search = key
                        style = curses.A_BOLD + curses.A_UNDERLINE
                index = color_list.index(search, 1)
                c_num = index
                color = color_list[c_num]

            self.addstr(4, x + 23, (color.replace('_', ' ').rjust(25)), self.colors[color] + style)  # testing
            self.addstr(4, x + 1, (item.replace('color', "").replace('_', ' ')).ljust(23),
                        self.colors['white_on_blue'] + curses.A_BOLD)  # testing
            self.hline(5, x, curses.ACS_HLINE, 49, self.config['color_bar'])
            # print vertical lines
            self.hline(4, x, curses.ACS_VLINE, 1, self.config['color_bar'])
            self.hline(4, x + 48, curses.ACS_VLINE, 1, self.config['color_bar'])
            # print corners
            self.hline(3, x, curses.ACS_ULCORNER, 1, self.config['color_bar'])
            self.hline(3, x + 48, curses.ACS_URCORNER, 1, self.config['color_bar'])
            self.hline(5, x, curses.ACS_LLCORNER, 1, self.config['color_bar'])
            self.hline(5, x + 48, curses.ACS_LRCORNER, 1, self.config['color_bar'])

            if style == curses.A_BOLD + curses.A_UNDERLINE:
                footer = '_Normal $ _Bold $ _Underline $ *b*O*t*h'
            elif style == curses.A_BOLD:
                footer = '_Normal $ *B*o*l*d $ _Underline $ b_Oth'
            elif style == curses.A_UNDERLINE:
                footer = '_Normal $ _Bold $ *U*n*d*e*r*l*i*n*e $ b_Oth'
            else:
                footer = '*N*o*r*m*a*l $ _Bold $ _Underline $ b_Oth'
            self.print_formatted_text(6, footer, 'center', self.width)
            self.addstr(8, x, sample_header, self.config['color_comment_centered'])  # Text types need to be changed?
            self.addstr(9, x, separator, self.config['color_comment_separator'])
            self.addstr(10, x, sample_left, self.config['color_comment_leftjust'])
            self.addstr(11, x, sample_right, self.config['color_comment_rightjust'])

            self.addstr(12, x, 'class', self.config['color_class'])
            self.addstr(12, x + 12, 'collapsed', self.config['color_class_reversed'])
            self.addstr(12, x + 28, 'print', self.config['color_commands'])
            self.addstr(12, x + 40, '#comment', self.config['color_comment'])

            self.addstr(13, x, 'def', self.config['color_functions'])
            self.addstr(13, x + 12, 'collapsed', self.config['color_functions_reversed'])
            self.addstr(13, x + 28, 'True', self.config['color_positive'])
            self.addstr(13, x + 40, 'False', self.config['color_negative'])

            self.addstr(14, x, "'quote'", self.config['color_quote_single'])
            self.addstr(14, x + 12, '"double"', self.config['color_quote_double'])
            self.addstr(14, x + 28, '"""doc"""', self.config['color_quote_triple'])

            self.addstr(14, x + 40, 'CONSTANT', self.config["color_constant"])

            self.addstr(15, x, '()!=[]+-', self.config['color_operator'])
            self.addstr(15, x + 12, 'normal text', self.config['color_normal'])
            self.addstr(15, x + 28, '0123456789', self.config['color_number'])
            self.addstr(15, x + 40, ' C.BLOCK', self.config['color_comment_block'])

            self.addstr(16, x, 'print ', self.config['color_entry_command'])
            self.addstr(16, x + 6, '"Entry line"', self.config['color_entry_quote'])
            self.addstr(16, x + 18, '; ', self.config['color_entry_dim'])
            self.addstr(16, x + 20, 'number ', self.config['color_entry'])
            self.addstr(16, x + 27, '= ', self.config['color_entry_dim'])
            self.addstr(16, x + 29, '100', self.config['color_entry_number'])
            self.addstr(16, x + 32, '; ', self.config['color_entry_dim'])
            self.addstr(16, x + 34, 'def ', self.config['color_entry_functions'])
            self.addstr(16, x + 38, '#comment  ', self.config['color_entry_comment'])

            self.addstr(17, x, 'class', self.config['color_entry_class'])
            self.addstr(17, x + 5, ': ', self.config['color_entry_dim'])
            self.addstr(17, x + 7, 'False', self.config['color_entry_negative'])
            self.addstr(17, x + 12, ', ', self.config['color_entry_dim'])
            self.addstr(17, x + 14, 'True', self.config['color_entry_positive'])
            self.addstr(17, x + 18, '; ', self.config['color_entry_dim'])
            self.addstr(17, x + 20, 'CONSTANT', self.config['color_entry_constant'])
            self.addstr(17, x + 28, '; ', self.config['color_entry_dim'])
            self.addstr(17, x + 30, '"""Triple Quote"""', self.config['color_entry_quote_triple'])

            self.addstr(18, x, '999 ', self.config['color_line_numbers'])
            self.addstr(18, x + 6, '....', self.config['color_tab_odd'])
            self.addstr(18, x + 10, '....', self.config['color_tab_even'])
            self.addstr(18, x + 14, '                                  ', self.config['color_background'])

            self.addstr(19, x + 12, 'Press [RETURN] when done!', self.config['color_warning'])
            self.refresh()
            c = self.getch()

            if c == curses.KEY_UP:
                i_num -= 1
                if i_num < 0:
                    i_num = 0
                c_num = 0
                # style_change = False
            elif c == curses.KEY_DOWN:
                i_num += 1
                if i_num > len(item_list) - 1:
                    i_num = len(item_list) - 1
                c_num = 0
                # style_change = False
            elif c == curses.KEY_LEFT:
                c_num -= 1
                if c_num < 1:
                    c_num = 1
                # style_change = False
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style

            elif c == curses.KEY_RIGHT:
                c_num += 1
                if c_num > len(color_list) - 1:
                    c_num = len(color_list) - 1
                # style_change = False
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style
            elif c in (ord('b'), ord('B')):
                style = curses.A_BOLD
                # style_change = True
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style
            elif c in (ord('u'), ord('U')):
                style = curses.A_UNDERLINE
                # style_change = True
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style
            elif c in (ord('n'), ord('N')):  # set style to normal
                style = 0
                # style_change = True  # no longer needed?
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style
            elif c in (ord('o'), ord('O')):
                style = curses.A_BOLD + curses.A_UNDERLINE
                # style_change = True
                self.config[item_list[i_num]] = self.colors[color_list[c_num]] + style

    def show_help(self):
        """Display help guide"""
        # global HELP_GUIDE, current_num, saved_since_edit
        # over_sized = False

        try:
            if self.editor.lines.db:
                del self.editor.lines.db
                self.editor.lines.db = {}
        except BareException:
            pass
        self.editor.current_num = 0
        total_rows = 0
        for i in range(0, len(HELP_GUIDE)):
            text = HELP_GUIDE[i]

            line = self.editor.lines.add(text)

            total_rows += (line.number_of_rows - 1)
            if line.number <= (self.height - 2) and self.editor.current_num + total_rows < (self.height - 2):
                self.editor.current_num += 1

        self.editor.current_num -= 1
        self.config.copy_settings()
        self.config['debug'] = False
        self.config['show_indent'] = False
        self.config['entry_highlighting'] = False
        self.config['syntax_highlighting'] = True
        self.config['format_comments'] = True
        self.config['live_syntax'] = True
        self.config['showSpaces'] = False
        self.config['splitscreen'] = False
        self.editor.lines.locked = True
        self.editor.status['help'] = True
        self.editor.saved_since_edit = True
        if self.width > 80:
            self.config['page_guide'] = 72
        else:
            self.config['page_guide'] = False
