'''
Basic wrappers for SerialUI built-in types.  

@summary: Wraps a few built-in SerialUI types with functionality to
          simplify Python integration and provides a Factory class.
@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

These classes wrap the built-in functionality of the types with a few convenience methods
and may be a good place to add enhancements.

@attention: in most cases, you'll want to derive your classes from the 'overrides' module instead,
or at least use the contents of that module as a basis for your own overrides.

Easiest way to use is 

 from pyserialui.wrappers import Factory
 menuitem = Factory.construct(SerialUI.tree()['SomeItem'])

then, you can do 
 menuitem.itemType()
which will show whether it's a command, input etc

Assuming it's an input request, then the wrapper will provide 
 menuitem.inputType()
to determine the type of data to feed to it's setValue() method.

'''

import SerialUI
import logging
import time
import pyserialui.types

log = logging.getLogger(__name__)

class ItemContainer(SerialUI.ItemContainer):
    def __init__(self, suiContainerObject:SerialUI.ItemContainer):
        super().__init__(key=suiContainerObject.key, id=suiContainerObject.id)
        
    def itemType(self):
        return pyserialui.types.Item(self.type)
    

    
class Input(SerialUI.Input):
    '''Use this class as a base for extensions to 
       SerialUI input request fields.
       
        class SomeInput(wrappers.Input):
            
            def myextrafunction(self):
                # do whatever you need to do with this self.value()
                SerialUI.println("done")
        
    '''
    def __init__(self, suiInputObject:SerialUI.Input):
        super().__init__(key=suiInputObject.key, id=suiInputObject.id)
        
    def itemType(self):
        return pyserialui.types.Item(self.type)
        
    def inputType(self):
        return pyserialui.types.Input(self.valuetype)
    
class InputEvent(Input):
    '''
        Input wrapper used specifically for Event requests, 
        in order to provide the eventDetails() method.
    '''
    
    def eventDetails(self) -> pyserialui.types.EventDetails:
        return pyserialui.types.EventDetails(self.value())


class Command(SerialUI.Command):
    '''
        Basic wrapper for commands.
    '''
    def __init__(self, suiCmdObject:SerialUI.Command):
        super().__init__(key=suiCmdObject.key, id=suiCmdObject.id)
        
    def itemType(self):
        return pyserialui.types.Item(self.type)


class Tracker(SerialUI.TrackedState):
    '''
        Tracker
        
        Basic wrapper for tracked state.
    '''
    def __init__(self, suiTrackStateObject:SerialUI.TrackedState):
        super().__init__(key=suiTrackStateObject.key, id=suiTrackStateObject.id)
        
    def itemType(self):
        return pyserialui.types.Item.TrackedState
    
    def stateType(self):
        return pyserialui.types.TrackedState(self.valuetype)
    
    
class Factory:
    '''
        Factory
        
        @summary: wrapper factory -- you should use this to construct
            more usable Python versions of SerialUI menu items.
            
            Simply: Factory.construct(SerialUI.tree()['SomeItem'])
    '''
    
    @classmethod 
    def constructInput(cls, suiItem:SerialUI.Input):
        if inputSUIItem.valuetype == SUIInputTypes.Event.value:
            return InputEvent(inputSUIItem)
        
        return Input(inputSUIItem)
    
    @classmethod
    def construct(cls, suiItem):
        suiItemType = type(suiItem)
        if suiItemType == list or suiItemType == dict:
            # special case to handle SerialUI.tree()
            # containers, rendered as dict/list
            # just leave them be:
            return suiItem
        
        if suiItemType == SerialUI.Input:
            return cls.constructInput(suiItem)
        if suiItemType == SerialUI.Command:
            return Command(suiItem)
        if suiItemType == SerialUI.ItemContainer:
            return ItemContainer(suiItem)
        if suiItemType == SerialUI.TrackedState:
            return Tracker(suiItem)
        log.error("Don't know how to handle this type %s" % str(suiItem))
        return None

