"""
Create and manipulate command lists.
"""

import shlex

class CmdList:
    """
    A list of shell commands.

    Attributes:
        commands: The list of commands to execute in the shell
        shell: The shell to execute the commands in
        separator: The separator use to separate the commands
    """

    def __init__(self, command, shell="/bin/bash -c", separator="&&"):

        shell = shell.strip()
        separator = separator.strip()

        if isinstance(command, str):
            self.commands = (command,)
            self.shell = shell
            self.separator = separator

        elif isinstance(command, self.__class__):
            self.commands = command.commands
            self.shell = command.shell
            self.separator = command.separator

        elif isinstance(command, (list, tuple)):
            if not command:
                raise ValueError("Cannot create command list from empty list or tuple")

            self.commands = tuple(str(c) for c in command)
            self.shell = shell
            self.separator = separator

        else:
            raise ValueError("Invalid type for command")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__!r})"

    def __str__(self):
        separator = " {} ".format(self.separator)
        commands_str = separator.join(self.commands)
        commands_str = shlex.quote(commands_str)
        return "{} {}".format(self.shell, commands_str)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __add__(self, other):
        if isinstance(other, self.__class__):
            ret = self.__class__(self)
            ret.commands += other.commands
            return ret
        if isinstance(other, str):
            ret = self.__class__(self)
            ret.commands += (other,)
            return ret

        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            ret = self.__class__(other)
            ret.commands += self.commands
            return ret
        if isinstance(other, str):
            ret = self.__class__(other)
            ret.commands += self.commands
            return ret

        return NotImplemented

    def to_popen_args(self):
        """
        Return the args parameter for subprocess.Popen

        Returns:
            A list of arguments for subprocess.Popen
        """

        return shlex.split(str(self))

def command_format(cmds, *args, **kwargs):
    """
    Create a CmdList from the command format string.

    This function constructs a command list from a single command string.

    cmd = command_format("string", *args, **kwargs)
    is roughly equivalent to
    cmd = "string".format(*args, **kwargs)

    Before the arguments are applied to the format string
    they are passed through shlex.quote to make them safe.

    command_format also creates a single shell command list
    for a multi line list of commands.

    >>> x = command_format('''
        command1
        command2
        command3
        ''')
    >>> y = CmdList(['command1', 'command2', 'command3'])
    >>> x == y
    True
    >>> str(x) == "/bin/bash -c 'command1 && command2 && command3'"
    True

    cmds can contain empty lines, which are ignored.

    Lines in cmds
    where the first non whitespace character is #
    are also ignored.

    Lines that end in with '\' are merged with the following line.

    Args:
        cmds: Command format string
        *args: list of positional arguments for the command format string
        **kwargs: list of keyword arguments for the command format string

    Returns:
        A CmdList instance
    """

    cmds = str(cmds)
    cmds = cmds.split("\n")
    cmds = [cmd.strip() for cmd in cmds]
    cmds = [cmd for cmd in cmds if cmd]
    cmds = [cmd for cmd in cmds if not cmd.startswith("#")]
    cmds = "\n".join(cmds)
    cmds = cmds.replace("\\\n", "")
    cmds = cmds.split("\n")

    args = [shlex.quote(str(x)) for x in args]
    kwargs = {k: shlex.quote(str(v)) for k, v in kwargs.items()}

    # Check for newlines
    for arg in args:
        if "\n" in arg:
            raise ValueError("Passing raw newlines via arguments is not supported")
    for v in kwargs.values():
        if "\n" in v:
            raise ValueError("Passing raw newlines via arguments is not supported")

    cmds = [cmd.format(*args, **kwargs) for cmd in cmds]

    return CmdList(cmds)
