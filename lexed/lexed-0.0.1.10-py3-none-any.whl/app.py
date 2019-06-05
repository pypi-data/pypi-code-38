import os
import sys

from .config import Config
from .console import curses
from .window import Window
from .meta import BareException


class LexEd:
    def __init__(self):
        self.clipboard = []
        self.config = Config(self)
        self.window = Window(self)
        self.editor = self.window.editor
        self.break_now = False

    def run(self):
        if self.window.height < 14 or self.window.width < 49:
            return 1, 'ERROR: lexed could not be launched, minimum terminal size of 50 x 15 required'

        # check for command line arguments
        args = sys.argv
        set_mode = False
        set_color = False
        help_flag = False
        set_protect_string = False
        read_only = False
        no_bold = False

        if '-' not in args[-1] and len(args) > 1 and not args[-1].startswith('['):  # check for file name/path
            path = args[-1]
            if '/' not in path:
                path = os.path.abspath(path)
        else:
            path = False

        if path and args and len(args) >= 2 and 's' in args[-2] and \
                args[-2].startswith('-') and not args[-2].startswith('--'):
            path = False

        if path and not os.path.exists(path):
            path = False  # New bit to stop program from crashing when path is bad
            self.editor.program_message = ' Error, file could not be loaded! '

        # check for flags
        flag_list = []
        for item in args:
            if item.startswith('-') and not item.startswith('--'):
                for letter in item:
                    if letter != '-':
                        flag_list.append(letter)
        # check for help flag
        if 'h' in flag_list or '--help' in args:
            help_flag = True
        # set mode and color
        if 't' in flag_list or '--text' in args:
            set_mode = 'text'
        elif 'p' in flag_list or '--python' in args:
            set_mode = 'python'
        if 'c' in flag_list or '--color' in args:
            set_color = 'color'
        elif 'm' in flag_list or '--mono' in args:
            set_color = 'monochrome'
        elif 'i' in flag_list or '--inverted' in args:
            set_color = 'inverted'
        if 'r' in flag_list or '--read' in args:
            read_only = True
        if 'n' in flag_list or '--nobold' in args:
            no_bold = True

        # FOR EDITING PURPOSES ONLY, REMOVE WHEN DONE!!!
        if "--source" in args and not path:
            path = args[0]  # lexed opens copy of itself for editing

        pos = 0
        if 's' in flag_list or '--string' in args:  # set protect string
            if '--string' in args:
                pos = args.index('--string')
                if path and len(args) >= 2 and 's' in args[-2] and args[-2] == '--string':
                    path = False
            else:
                if path and len(args) >= 2 and 's' in args[-2] and args[-2].startswith('-'):
                    path = False
                for i in range(0, len(args)):
                    item = args[i]
                    if item.startswith('-') and not item.startswith('--') and 's' in item:
                        pos = i

            flag_error = """
            ERROR:\n
            Argument required by string flag (maximum size 4 characters)\n
            Example: lexed -s '::' myfile.txt\n
            """
            try:
                set_protect_string = args[pos + 1]
                # next part was modified to safeguard against pathname becoming protect string
                if len(set_protect_string) < 5:
                    self.config[
                        "inline_commands"] = "protected"  # set to "protected" to protect commands with protect string
                    self.config["protect_string"] = set_protect_string
                else:
                    self.window.curses_off()
                    print(flag_error)
                    sys.exit()
            except BareException:
                self.window.curses_off()
                print(flag_error)
                sys.exit()

        if no_bold:
            self.config.set_default_settings(False, False)

        if set_mode == "text":
            self.config.settings.update({
                "entry_highlighting": False,
                "syntax_highlighting": False,
                "live_syntax": False,
                "debug": False,
                "collapse_functions": False,
                "showSpaces": False,
                "show_indent": False,
                "inline_commands": "protected",  # set to "protected" to protect commands with protect string
                "format_comments": True,
                "protect_string": set_protect_string or self.config["protect_string"],
            })
        elif set_mode == "python":
            self.config.settings.update({
                "entry_highlighting": True,
                "syntax_highlighting": True,
                "live_syntax": True,
                "debug": True,
                "show_indent": True,
                # set to "protected" to protect commands with protect string
                "inline_commands": self.config["inline_commands"] or True,
                "format_comments": True,
            })
        if set_color == "color":
            self.config.settings.update({
                "display_color": True,
                "default_colors": True,
            })
        elif set_color == "monochrome":
            self.config.settings["display_color"] = False
            self.config.set_default_settings(True, True)
        elif set_color == "inverted":
            self.config.settings["display_color"] = False
            self.config.invert_monochrome()
            self.config.set_default_settings(True, True)

        # Turn on color
        if self.config["display_color"] and self.config["default_colors"]:
            self.window.color_on(True)  # default colors
        elif self.config["display_color"]:
            self.window.color_on()  # user defined colors
        # Clear screen and draw bar
        if self.config["color_background"]:
            self.window.print_background()
        self.window.hline(1, 0, curses.ACS_HLINE, self.window.width, self.config["color_bar"])
        # Adjust page guide if necessary
        if self.config["page_guide"] > self.window.width - 7:
            self.config["page_guide"] = False
        # Load file or create new doc
        # self.editor.lines.db = {}  # create new doc (moved to fix bug)
        # self.editor.lines.add('')
        self.editor.current_num = 1
        self.editor.save_path = ''
        self.editor.saved_since_edit = True

        if help_flag:
            self.window.show_help()
            # set_mode = False
        elif path:  # load file if path exists
            # print 'splash screen' while loading
            half_height = int(self.window.height / 2)
            half_width = int(self.window.width / 2)
            self.window.clear()
            self.window.hline(1, 0, curses.ACS_HLINE, self.window.width, self.config["color_bar"])
            self.window.addstr(half_height - 1, half_width - 11, "                       ",
                               self.config["color_message"])
            self.window.addstr(half_height, half_width - 11, "    lexed  1.04    ", self.config["color_message"])
            self.window.addstr(half_height + 1, half_width - 11, "                       ",
                               self.config["color_message"])
            if read_only:  # load read only file
                self.editor.load(path, True)
            else:  # load file for editing
                self.editor.load(path)

        if not help_flag and not self.editor.lines.locked:
            self.editor.current_num = self.editor.lines.total
        self.editor.current_line = self.editor.lines.db[self.editor.current_num]

        self.editor.update_que()

        # indent_level = 0
        # c = 0

        # Begin Main Loop
        self.editor.run_editor()

        # @
        # # Version: 1.04
        # # License: Open Source
        # # Edited on 07/25/08 09:54:26 PM
        # # -------------------------------------
        # # Fixed errorTest() bug that caused crashes when loading small files
        # @
