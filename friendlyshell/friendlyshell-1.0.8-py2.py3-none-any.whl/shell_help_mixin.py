"""Mixin class that adds online help to a friendly shell"""
import inspect
from textwrap import wrap
import tabulate


class ShellHelpMixin(object):
    """Mixin class to be added to any friendly shell to add online help"""
    # Number of characters the online help output should be wrapped to
    WRAP_WIDTH = 80

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super(ShellHelpMixin, self).__init__(*args, **kwargs)

    def _description_wrap(self, command_names, help_examples):
        """Calculates the maximum width for descriptive text in our help output

        :param list command_names: list of command names to render
        :param list help_examples: list of extended help examples to render
        :return:
            number of characters remaining for rendering descriptive text
            may be 0 if there is no available room for rendering descriptions
        :rtype: :class:`int`
        """
        longest_cmd = 0
        for cur_cmd in command_names:
            if len(cur_cmd) > longest_cmd:
                longest_cmd = len(cur_cmd)

        longest_extended_help = 0
        for cur_help in help_examples:
            if len(cur_help) > longest_extended_help:
                longest_extended_help = len(cur_help)

        other_fields_width = longest_cmd + longest_extended_help + 2
        if other_fields_width > self.WRAP_WIDTH:
            return 0
        return self.WRAP_WIDTH - other_fields_width

    def _list_commands(self):
        """Displays a list of supported commands"""
        all_methods = inspect.getmembers(self, inspect.ismethod)
        command_list = {
            'Command': [],
            'Description': [],
            'Extended Help': [],
        }
        for cur_method in all_methods:
            # Each method definition is a 2-tuple, with the first element being
            # the name of the method and the second a reference to the method
            # object
            method_name = cur_method[0]
            method_obj = cur_method[1]

            self.debug('Checking for command method %s', method_name)

            # Methods that start with 'do_' are interpreted as command operator
            if method_name.startswith('do_'):
                self.debug("Found a do command %s", method_name)
                # Extrapolate the command name by removing the 'do_' prefix
                cmd_name = cur_method[0][3:]

                # Generate our help data
                command_list['Command'].append(cmd_name)
                alias_method_name = "alias_" + cmd_name
                if hasattr(self, alias_method_name):
                    alias_method = getattr(self, alias_method_name)
                    command_list['Command'][-1] += \
                        " ({0})".format(alias_method())

                doc_string = inspect.getdoc(method_obj) or ''
                doc_string = doc_string.replace("\n", " ")
                command_list['Description'].append(doc_string)

                if hasattr(self, method_name.replace('do_', 'help_')):
                    self.debug(
                        "Found an associated help method %s",
                        method_name.replace('do_', 'help_')
                    )
                    # NOTE:
                    # For the sake of online help, we'll assume that class
                    # attributes with 'help_' in their name are methods which
                    # can be called to display verbose help. We can add
                    # verification logic for this elsewhere when necessary
                    command_list['Extended Help'].append(
                        '`help ' + cmd_name + '`')
                else:
                    command_list['Extended Help'].append('N/A')


        wrap_width = self._description_wrap(
            command_list['Command'],
            command_list['Extended Help'])

        if wrap_width == 0:
            self.error("Insufficient space to render help. Consider enlarging "\
                       "the width of your help output.")
            return

        new_desc = list()
        for cur_cmd in command_list['Description']:
            new_desc.append("\n".join(wrap(cur_cmd, wrap_width)))
        command_list['Description'] = new_desc

        self.info(tabulate.tabulate(command_list, headers="keys"))

    def do_help(self, arg=None):
        """Online help generation (this command)"""
        # no command given, show available commands
        if arg is None:
            self.debug("Showing default help output...")
            self._list_commands()
            return

        # Sanity check: make sure we're asking for help for a command
        # that actually exists
        cmd_method_name = 'do_' + arg
        if not hasattr(self, cmd_method_name):
            self.error("Command does not exist: %s", arg)
            return
        cmd_method = getattr(self, cmd_method_name)
        if not inspect.ismethod(cmd_method) and \
            not inspect.isfunction(cmd_method):
            self.error(
                'Error: definition "%s" in derived class must be a method. '
                'Check implementation',
                cmd_method_name)
            return

        # Next, extract summary information from the doc strings associated
        # with the command method
        docs = ""
        tmp_docs = cmd_method.__doc__ or ""
        for cur_line in tmp_docs.split("\n"):
            if not cur_line.strip():
                continue
            docs += cur_line.strip() + " "

        # Next, see if there's a "help_<cmd>" method on the class
        method_name = 'help_' + arg
        if hasattr(self, method_name):
            func = getattr(self, method_name)
            if not inspect.ismethod(func) and not inspect.isfunction(func):
                self.error(
                    'Error: definition "%s" in derived class must be a method. '
                    'Check implementation',
                    method_name)
                return

            docs += "\n\n" + func()

        if not docs:
            self.info('No online help for command "%s"', arg)
            return

        for cur_line in docs.split("\n"):
            self.info("\n".join(wrap(cur_line, self.WRAP_WIDTH)))

    def complete_help(self, parser, parameter_index):
        """Automatic completion method for the 'help' command"""
        return self._complete_command_names(
            parser[parameter_index])

    def help_help(self):
        """Generates inline help for the 'help' command"""
        retval = [
            "Online help generation tool",
            "Running 'help' with no parameters displays a list of supported "
            "commands",
            "Passing any supported command to 'help' provides detailed help on "
            "the command",
            "example: " + self.prompt + "help exit"
            ]
        return '\n'.join(retval)

    @staticmethod
    def alias_help():
        """Gets short hand character for the help command

        :rtype: :class:`str`
        """
        return "?"
