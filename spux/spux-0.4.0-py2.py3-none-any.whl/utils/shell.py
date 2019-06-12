import subprocess
import os

def execute (command, directory = None, verbosity = 1, executable = None):
    """Execute an application command (including any arguments) in a command line shell."""

    PIPE = subprocess.PIPE
    if verbosity:
        print ('  : -> Executing: %s' % command)
    process = subprocess.Popen ([command], cwd = directory, shell = True, stdout = PIPE, stderr = PIPE, env = os.environ.copy (), executable=executable)
    output, error = process.communicate ()

    if verbosity:
        if process.returncode == 0:
            print ('  : -> Shell command done.')
        else:
            print ('  : -> Shell command returned a non-zero exit code.')
            print ('  : -> The standard output and the standard error are printed below.')
            print ('  : -> STDOUT:')
            print (output.decode ('ascii'))
            print ('  : -> STDERR:')
            print (error.decode ('ascii'))

    return process.returncode