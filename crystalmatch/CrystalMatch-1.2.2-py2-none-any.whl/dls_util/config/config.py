import logging
import os


class Config:
    """ Class for making simple persistent config/options for a program. To use, you should subclass
    and call the add() method for each option to be added and then call the initialize_from_file()
    method to load the saved options from the specified config file:

         class MyConfig(Config):
             def __init__(self, file):
                 Config.__init__(self, file)

                 self.int_option1 = self.add(IntConfigItem, "Int Option", default=35)
                 self.dir_option1 = self.add(DirectoryConfigItem, "Dir Option", default="../my_dir/")
                 self.color_option1 = self.add(ColorConfigItem, "Color Option", Color.red())

                 self.initialize_from_file()

    The type of the config item supplied as the first argument to add() determines how the item
    behaves (any formatting done, how it is read from and print to file, etc). To add handling for new
    custom types, subclass ConfigItem and override the appropriate functions.

    Note to access the value of an option from a client class, call the value() method of the item.:

         my_config.dir_option1.value()

    The ConfigDialog class is also provided, which is intended to be used with this class in order to
    create simple Qt4 Dialog windows for editing these options.
    """

    DELIMITER = "="
    COMMENT = "#"
    LINE_LENGTH = 100

    def __init__(self, file_path):
        self._file = file_path
        self._title = None
        self._comment = None
        self._items = []

    def title(self): return self._title

    def comment(self): return self._comment

    def set_title(self, title):
        """ Title that will be displayed in config file and dialog. """
        self._title = title

    def set_comment(self, comment):
        """ General comment or instructions about this set of options. Individual config items can also
        each have their own comment. The comment is displayed in the config file and as a tooltip in the
        dialog. """
        self._comment = comment

    def initialize_from_file(self):
        """ Open and parse the config file provided in the constructor. This should only be called after
        the relevant ConfigItems hasve been set up by adding them with add(). """
        self.reset_all()
        self._load_from_file(self._file)

    def add(self, cls, tag, default, extra_arg=None):
        """ Add a new option of a specified type to this config.

        Parameters
        ----------
        cls - The config type; should be subclass of ConfigItem
        tag - the text string that uniquely labels this option, will appear in file and config dialog
        default - The default value for this option
        extra_arg - Additional argument required by some ConfigItems
        """
        if extra_arg is None:
            item = cls(tag, default)
        else:
            item = cls(tag, default, extra_arg)
        self._items.append(item)
        return item

    def reset_all(self):
        """ Set the value of every option to its default. """
        for item in self._items:
            item.reset()

    def save_to_file(self):
        """ Save the current options to the config file specified in the constructor. """
        if not os.path.exists(os.path.dirname(self._file)):
            os.makedirs(os.path.dirname(self._file))

        with open(self._file, 'w') as f:
            f.write(self._make_file_header())
            for item in self._items:
                f.write("\n\n" + item.to_file_string())

    def _make_file_header(self):
        """ Create string header to be displayed in the config file. Includes the title and comment. """
        header = ""
        if self._title is not None:
            num_pad = max(2, self.LINE_LENGTH - len(self._title)) - 2
            banner = "-" * int(num_pad / 2)
            header += "# {} {} {}\n".format(banner, self._title, banner)

        if self._comment is not None:
            comment_lines = self.create_comment_lines(self._comment)
            header += "".join(comment_lines)

        return header

    def _load_from_file(self, file_path):
        """ Load options from the config file specified in the constructor. """
        if not os.path.isfile(file_path):
            self.save_to_file()
            return

        with open(file_path) as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(self.COMMENT) or line.strip() == "":
                    continue

                try:
                    self._parse_line(line)
                except ValueError:
                    logging.warning("Failed to parse config line: '{}'".format(line))

    def _parse_line(self, line):
        """ Parse a line from a config file, setting the value of the relevant option. """
        tokens = line.strip().split(Config.DELIMITER)
        tag, value = tuple(tokens)
        for item in self._items:
            if tag == item.tag():
                item.from_file_string(value)
                break

    def all_to_json(self):
        all = dict()
        for item in self._items:
            all.update(item.to_json())
        return all

    @staticmethod
    def create_comment_lines(string):
        """ Convert string into lines of comments to be displayed in a file. Wraps the string to an
        appropriate line length and adds the comment character '#' at the start of each line. """
        lines = Config._string_to_wrapped_lines(string, Config.LINE_LENGTH-2)
        for i in range(len(lines)):
            lines[i] = Config.COMMENT + " " + lines[i] + "\n"

        return lines

    @staticmethod
    def _string_to_wrapped_lines(string, line_length):
        """ Takes a string and wraps it to fit the specified line length by breaking the string
        into words and inserting new lines as appropriate. """
        words = string.split()
        lines = [words[0]]

        for word in words[1:]:
            if len(lines[-1]) + len(word) > line_length:
                lines.append("")

            lines[-1] += " " + word

        return lines
