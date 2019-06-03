import subprocess, sys, urllib
from . import cnf

def ell(programName, *args):
    
    """Takes program name and argument(s), 
    executes in shell."""

    if cnf.platform == 'linux':
        subprocess.Popen([programName, *args])
    
    elif cnf.platform == 'win32':    
        # escape arguments ampersands for Windows
        new_args = []
        for arg in args:
            new_args.append(arg.replace('&','^&'))
        # special case for Windows: Chrome is invoked with 'start chrome'
        if 'chrome' in programName:    
            subprocess.Popen(['start', 'chrome', *new_args], shell=True)
        # try default (Linux) method and hope for program path existence
        else: 
            subprocess.Popen([programName, *new_args], shell=True)



