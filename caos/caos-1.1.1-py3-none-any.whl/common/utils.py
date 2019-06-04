import os
import io
from caos.common import constants
from contextlib import redirect_stdout

#OS Utils
def get_os_type() -> str:
    platforms = {
        'posix' : constants._LINUX_UNIX,
        'nt' : constants._WINDOWS
    }
    if os.name not in platforms:
        raise OSError("Operating system not supported")
    
    return platforms[os.name]

#String Utils
def single_quote_text(input:str) -> str:
    return "'{0}'".format(input)

def double_quote_text(input:str) -> str:
    return '"{0}"' .format(input)

#Callabale Utils
def get_func_without_params_stdout(func: callable) -> str:
    with io.StringIO() as buf, redirect_stdout(buf):
        func()
        return buf.getvalue()[:-1] #Remove the last line return added by the print() function
