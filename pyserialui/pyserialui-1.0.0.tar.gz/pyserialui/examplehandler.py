'''
    Example SerialUI Python handler module.
    
    @author: Pat Deegan
    @copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com
    @summary: Sample SerialUIHandler to excercise a few functions in Python
    
    This example assumes you have a SerialUI driver program setup with only the top-level
    menu and these items within:
        - ACommand -- some command that is to do something
        - NumberInput -- an input for some numeric value
        - TextInput -- an input for some text
    
    It will:
        * override the command response (triggered()), using a class
        * override the NumberInput modified callback (changed()) using a class
        * override the TextInput modified callback, directly on the input in the tree
        * setup a basic authenticator to restrict access with a hardcoded password
        * implement a boring user presence heartbeat, that outputs some text
    
'''
# import SerialUI -- this is how we access the C/C++ side, which holds 
# the menu tree/items/etc
import SerialUI

# overrides -- this has basic python wrappers/implementations
from pyserialui.overrides import (Input, Command, AuthStorage, AuthValidator)
# from sqliteauth import (AuthStorage, AuthValidator)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# MyNumberInput -- we'll use this to implement 
# changed() callback on the 'NumberInput' input request
class MyNumberInput(Input):
    '''
        The overrides.Input has default implementations 
        for supported methods.  
        We'll just implement changed() so we can see some 
        custom message.
    '''
    def changed(self):
        reportstr = "OOOOOh number input changed to %s" % str(self.value())
        log.debug(reportstr)
        print(reportstr) #output here
        SerialUI.println(reportstr) # output to client
        



# MyCommand -- we'll use this to implement 
# triggered() callback on the 'ACommand' command item
class MyCommand(Command):
    def triggered(self):
        reportstr = "Trigger warning! ahem.  Command triggered"
        log.debug(reportstr)
        print(reportstr) #output here
        SerialUI.println(reportstr) # output to client
        



def IsThisValid(val):
    '''
        stand alone input validator.
    '''
    print("Checking if '%s' is valid input... YES!" % str(val))
    return True # we always say yes




class SerialUIHandler:
    '''
        SerialUIHandler
        @summary: Having a 'SerialUIHandler' class is the one requirement to
        using loadable modules with SerialUI.
        
        SerialUIHandler is the entry point for SerialUI python support.
        An instance of this class will be created when the module is loaded.
        It is used to:
            - perform initialization, setup callbacks, etc
            - hold onto references to python objects used to override inputs/commands
            - implement specifically-named methods to provide functionality (e.g. 
                the 'heartbeat' method), as required
        
    '''
    def __init__(self):
        '''
            SerialUIHandler init 
            @summary: called when the module is loaded (after setup, before main loop)
        '''
        print("SerialUIHandler init called!")
        # restrict access.  First create a basic validator
        self.validator = AuthValidator(AuthStorage('asecret'))
        # now set this validator as the authenticator for the system
        SerialUI.setAuthValidator(self.validator)
        
        # override the "NumberInput" menu item's callbacks
        if self.getMenuItem('NumberInput') is None:
            print("No 'NumberInput' menu item found here ... skipping")
        else:
            # it does exist.  All we need to do is create an instance of 
            # our override class by passing it the tree item we want to affect
            # AND make sure we hold on to a reference to this object... If it 
            # is garbage-collected, our override no longer applies
            self.my_number_input = MyNumberInput(self.getMenuItem('NumberInput'))
            
            
        # override the "ACommand" menu item
        if self.getMenuItem('ACommand') is None:
            print("No 'ACommand' menu item found here... skipping")
        else:
            # got it.  Same as for input, above.  All we do is 
            # instantiate our override and hold on to the reference
            self.my_command_obj = MyCommand(self.getMenuItem('ACommand'))
            
        # so far, we've implemented our overrides by defining a class
        # and creating an instance.  Another method is to act on the 
        # SerialUI.tree() items themselves.
        textInput = self.getMenuItem('TextInput')
        if textInput is None:
            print("Hm, can't find 'TextInput' item in tree... skipping")
        else:
            # ok, have the item in the tree...
            # let's just override its validator
            textInput.setValidator(IsThisValid)
            
    
    def loaded(self):
        print("Module now completely loaded/setup and ready to go")
        
    def userEnter(self):
        ''' userEnter
            @summary: if defined, this method will be called when a user arrives/connects.
        '''
        print("User has arrived!")
    def userExit(self):
        ''' userExit
            @summary: if defined, this method will be called when a user leaves/disconnects.
        '''
        print("User has left!")

    def heartbeat(self):
        '''
            heartbeat
            @summary: simply defining this function will setup a user presence heartbeat
            Called periodically while a user is interacting with the device.
            
        '''
        print("Beating heart")
        
        
    def getMenuItem(self, itmName:str):
        '''
            Can't be certain this module will be run with a 
            suitably setup program, so getMenuItem() is here 
            just to safely check for, and return, items from the 
            SerialUI tree.
            
            Probably always a good idea to use such a method, but 
            you could also just do things like
            blah = MyOverride(SerialUI.tree()['An Item Im certain is there'])
            or even
            SerialUI.tree()['A Command Im certain is there'].setOnTriggered(somefunction)
            
        '''
        itemTree = SerialUI.tree()
        if itmName in itemTree:
            return itemTree[itmName]
        return None
        




