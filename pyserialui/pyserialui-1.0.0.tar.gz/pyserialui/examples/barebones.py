'''
    barebones.py
    
    @author: Pat Deegan
    @copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com
    @summary: Barebones python implementation for SerialUI/Device Druid
    
    This example relies only on what's already built into libserialui.  All
    the functionality here is available, through the built-in SerialUI module,
    to any handler launched within a program created by the druid builder
    https://devicedruid.com/builder/
    
    
    Launching a SerialUI program by specifying this file as the module
    to load:
        /path/to/myprogram -m /path/to/barebones.py
    
    will:
        - assign one of two callbacks to each command,
          which will be called whenever a user issues the command from druid
          
        - assign one of two callbacks to each input request,
          which will be called whenever a user changes an input value using druid
    
    
    

'''

import SerialUI
import logging


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def global_command_callback(theCommand):
    log.info("Command %s!" % theCommand.key)
    outstr ="Command '%s' [%i] triggered (global callback)" %  (
            theCommand.key, 
            theCommand.id)
    log.debug(outstr)
    SerialUI.println(outstr)
    
def global_inputchanged_callback(theInput):
    log.info("Input %s change!" % theInput.key)
    outstr ="Input '%s' [%i] changed to '%s' (global callback)" %  (
            theInput.key, 
            theInput.id,
            str(theInput.value()))
    log.debug(outstr)
    SerialUI.println(outstr)
    


class SerialUIHandler:
    '''
        SerialUIHandler
        
        @summary: SerialUIHandler is the loadable Python module entry point
        
        
        All modules loaded with the -m switch need to include a SerialUIHandler
        class.  The entire module may be contained within this one file, 
        or it may be split into a module system of packages, but whatever is passed to
            /path/to/myprogram -m /path/to/whatever.py
        need a SerialUIHandler class defined.
        
        That's it.  Methods may be provided within, to implement features 
        (e.g. user heartbeat, user presence, etc) and do anything useful, but 
        they are all optional.
    '''
            
    def __init__(self):
        '''
            init
            @summary: called when the program is launched an to load the Python handler
        '''
        log.debug("SerialUIHandler module construction")
        self.command_counter = 0
        self.input_counter = 0
        
    def loaded(self):
        '''
            loaded 
            
            @summary: ready to begin, perform extra setup here
            
            Call once SerialUI is ready to start processing users.  At this stage,
            you're guaranteed to have access to the items through
                - SerialUI.tree()
                - SerialUI.top() etc
            and the tracked states (SerialUI.trackers()).
        '''
        # I don't know what your SerialUI.tree() actually contains
        # so we'll do it dynamically, by crawling the entire menu
        # tree
        log.info("Module loaded")
        log.debug("Crawling the items to setup callbacks")
        # foreachItem will call the provided function/method
        # for each menu item found (depth first)
        # return False in that function to stop going any deeper
        SerialUI.foreachItem(self.crawler_callback)

    
    
    def crawler_callback(self, menuitem):
        ''' crawler_callback
            @summary: will be called for each item in the menu tree.
            We'll use this to set the triggered callbacks for commands
            and the changed callbacks for inputs.
        '''
        if type(menuitem) == SerialUI.Command:
            self.command_counter += 1
            if self.command_counter % 2:
                # we'll use the global callback, up there
                menuitem.setOnTriggered(global_command_callback)
            else:
                # this time we'll use the instance method, down here
                menuitem.setOnTriggered(self.command_callback)
        elif type(menuitem) == SerialUI.Input:
            self.input_counter += 1
            if self.input_counter % 2:
                # we use the global callback, up there
                menuitem.setOnChange(global_inputchanged_callback)
            else:
                # for this input, we'll use the instance method, just 'cause
                menuitem.setOnChange(self.input_changed)
        
        # return True to continue crawling recursively
        # if you return False (or None, or nothing, or anything not truthy), 
        # it'll stop going through the tree
        return True
    
    def command_callback(self, cmd):
        log.info("Command %s!" % cmd.key)
        outstr ="Command '%s' [%i] triggered (handler callback)" %  (
                cmd.key, 
                cmd.id)
        log.debug(outstr)
        SerialUI.println(outstr)
    
    def input_changed(self, inputObj):
        log.info("Input %s change!" % inputObj.key)
        outstr ="Input '%s' [%i] changed to '%s' (handler callback)" %  (
                inputObj.key, 
                inputObj.id,
                str(inputObj.value()))
        log.debug(outstr)
        SerialUI.println(outstr)
        
        