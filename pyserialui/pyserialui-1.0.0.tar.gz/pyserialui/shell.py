'''
    pyserialui shell
    Launching a SerialUI program by specifying this file as the module
    to load:
        /path/to/myprogram -m /path/to/shell.py
    will
        - initialize and setup the SerialUI menu structure
        - immediately run the REPL/interactive console
        
    In this console, you will have access to the built-in 
    SerialUI module (and hence the functions provided, such as
    SerialUI.tree() or SerialUI.top()), as well as a few other useful
    objects and modules.
    
    Use dir() or peek into source, here.
    
@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

'''

import SerialUI
from pyserialui.overrides import (Input, Command, AuthStorage, AuthValidator)
from pyserialui.interpreter import runInterpreter
import pprint
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
class SerialUIHandler:
    def __init__(self):
        log.debug("Debug/shell module loaded")
        self.printer = pprint.PrettyPrinter(indent=3)
        # launch debug shell immediately
        
    def loaded(self):
        self.debug()
        

    def showTree(self):
        self.printer.pprint(SerialUI.tree())
    
    def extensionGlobalVariables(self):
        # override and return a dict with
        # 'GLOBVARNAME' = whatever
        # to have 'GLOBVARNAME' available at
        # global scope in your shell.
        return dict() 
    
    def globalVariables(self):
        gVars =  {'self': self, 
            'AuthStorage':AuthStorage, 
            'AuthValidator': AuthValidator,
            'Command':Command,
            'Input':Input,
             }
        extVars = self.extensionGlobalVariables()
        for v in extVars:
            gVars[v] = extVars[v]
        
        return gVars
    
    def debug(self):
        log.info("Launching interpreter")
        print("\n\n\nDebug interpreter launching. Use \n")
        print("\tself: to access this module, e.g.")
        print("\t\tself.showTree()")
        print("\tSerialUI: to access SerialUI function, e.g.")
        print("\t\tSerialUI.tree(), SerialUI.top(), etc.")
        print("\n\n")
        runInterpreter(self.globalVariables())
