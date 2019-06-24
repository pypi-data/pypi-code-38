class CommandResult(object):
    """Encapsulate result from a subprocess call."""

    def __init__(self, completed_process=None, returncode=None, output=None, strip_leading_whitespace=True):
        """Convert a completed_process object into a ShellResult."""
        if completed_process:
            self.returncode = completed_process.returncode
            if completed_process.stderr:
                self.output = completed_process.stderr.decode('utf-8').rstrip()
            else:
                self.output = completed_process.stdout.decode('utf-8').rstrip()
            if strip_leading_whitespace:
                self.output = self.output.strip()
        else:
            self.returncode = returncode
            self.output = output

    def __str__(self):
        return "CommandResult({},{})".format(self.returncode, self.output)

    def __repr__(self):
        return "CommandResult({},{})".format(self.returncode, self.output)

    def success(self):
        return self.returncode == 0

    def failure(self):
        return not self.success()


class CommandException(Exception):
    """ Instead of returning a CommandResult for all actions, we can also return 
    a result normally and throw a CommandException instead on error. """
    
    def __init__(self, command_result):
        self.command_result = command_result
