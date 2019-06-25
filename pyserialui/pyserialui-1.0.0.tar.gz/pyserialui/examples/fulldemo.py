'''
    fulldemo.py
    
    @author: Pat Deegan
    @copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com
    @summary: fulldemo python implementation for SerialUI/Device Druid
    
    This example relies on pyserialui to provide enhanced functionality.
    It also implements more handler methods than the barebones example,
    such as heartbeat and user enter/exit.
    
    
    Launching a SerialUI program by specifying this file as the module
    to load:
        /path/to/myprogram -m /path/to/barebones.py
    
    It will:
        - crawl the entire menu structure for inputs/commands
        - instantiate an object for each, which overrides callbacks
        - provide output locally and to remote user when commands are
          triggered or inputs changed.
          
    The main difference with the barebones sample is that, rather than
    setting callbacks directly on the menu items, it defines a few 
    classes (e.g. "MyCommand", below) and then instantiates those with
    the relevant SerialUI Command or Input.  
    
    This allows you to leverage OO power to implement the functionality
    you want when device users issue command or change settings.
    
    

'''

import SerialUI
import logging


import pyserialui.wrappers as wrappers
from pyserialui.types import Input as InputTypes

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)




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
        self.iteminstances = [] # we'll hold on to object here
        
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
        
        SerialUI.setHeartbeatPeriod(2000) # don't want to be bothered too often
        
    
    def heartbeat(self):
        '''
            heartbeat
            @summary: called periodically when user is around, if defined
        '''
        log.debug("Heartbeat beats.")
        
    
    def userEnter(self):
        ''' userEnter
            @summary: if defined, this method will be called when a user arrives/connects.
        '''
        log.info("User has arrived!")
        
    def userExit(self):
        ''' userExit
            @summary: if defined, this method will be called when a user leaves/disconnects.
        '''
        log.info("User has left!")

    
    
    def crawler_callback(self, menuitem):
        ''' crawler_callback
            @summary: will be called for each item in the menu tree.
            We'll use this to create instances that override methods 
            of interest
        '''
        # we construct an instance of the appropriate class
        # using "MyFactory" (below).  The important thing is that we
        # need to hold onto a reference to the object, otherwise it'll
        # be garbage collected before we can do anything useful
        wrappedItem = MyFactory.construct(menuitem)
        if wrappedItem is not None:
            log.debug("Created a wrapper instance around a %s" % str(wrappedItem.itemType()))
            self.iteminstances.append(wrappedItem)
        
        
        # return True to continue crawling recursively
        # if you return False (or None, or nothing, or anything not truthy), 
        # it'll stop going through the tree
        return True
    
    
class MyFactory:
    '''
        MyFactory
        
        @summary: used to create instances of our custom classes for commands/inputs.
        
    '''
    @classmethod
    def construct(cls, suiItem):
        # we want to wrap the item with a useful 
        # implementation class.  Which class depends on the type of 
        # of menu item we just got
        if type(suiItem) == SerialUI.Input:
            return cls.constructInput(suiItem)
        
        if type(suiItem) == SerialUI.Command:
            return cls.constructCommand(suiItem)
        
    @classmethod
    def constructInput(cls, itm:SerialUI.Input):
        if itm.valuetype == InputTypes.Event.value:
            return MyInputEvent(itm)
        
        return MyInput(itm)
    
    @classmethod
    def constructCommand(cls, itm:SerialUI.Command):
        return MyCommand(itm)
    


######### 

class MyCommand(wrappers.Command):
    '''
        MyCommand
        @summary: our custom wrapper for command items.
        
        Mainly useful to override the triggered() method
        to do something interesting.
        
    '''
    def triggered(self):
        outstr = 'Command %s triggered' % self.key
        
        log.info(outstr) # local logging
        SerialUI.println(outstr) # send to user too
        

class MyInput(wrappers.Input):
    '''
        @summary: override for user inputs
    '''
    def changed(self):
        ''' 
            @summary: changed() -- called whenever this input is modified.
            
        '''
        outstr = 'Input %s (which is an %s) is now "%s"' % (
            self.key,
            str(self.inputType()),
            str(self.value())
        )
        log.info(outstr) # local output
        SerialUI.println(outstr) # send to user
    

class MyInputEvent(wrappers.InputEvent):
    '''
        @summary: special override for event inputs
    '''
    def changed(self):
        ''' 
            @summary: changed() -- called whenever this event is modified.
            
            The event item value() is a number that doesn't mean all that 
            much, at first glance.
            
            We use the wrappers.InputEvent.eventDetails() to get something
            more useful.
        '''
        
        evtDetails = self.eventDetails()
        
        outstr = 'Input %s is now scheduled for %s-%s (current: %s)' % (
            self.key,
            str(evtDetails.startTime()),
            str(evtDetails.endTime()),
            str(evtDetails.isCurrentNow())
        )
        log.info(outstr) # local output
        SerialUI.println(outstr) # send to user