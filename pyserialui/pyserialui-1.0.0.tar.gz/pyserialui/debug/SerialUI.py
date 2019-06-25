'''
SerialUI 

@summary: Debug version of the built-in SerialUI module

@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

@attention: this isn't for general use, just desktop dev outside SUI env.

'''

def debugOut(msg):
    global print
    print("SerialUI(DEBUG) %s" % str(msg))

class BaseMenuItem:
    def __init__(self, key, id):
        self.key = key
        self.id = id


class Input(BaseMenuItem):
    def __init__(self):
        super().__init__('SomeInput', 2)
        self.val = None
    def setValidator(self, cb):
        debugOut("Input setValidator")
        return True
    def setOnChange(self, cb):
        debugOut("Input setOnChange")
        return True
    def value(self):
        debugOut("Input value")
        return self.val
    def setValue(self, setTo):
        debugOut("Input setValue")
        self.val = setTo
        return True
    
        
        
        
class ItemContainer(BaseMenuItem):
    def __init__(self):
        super().__init__('TOP', 1)
    def children(self):
        return []

class Command(BaseMenuItem):
    def __init__(self):
        super().__init__('SomeCommand', 3)
        
    def setOnTriggered(self, cb):
        debugOut("Input setOnTriggered")
        return True
    

class TrackedState:
    def __init__(self):
        self.val = None
    def value(self):
        debugOut("TrackedState value")
        return self.val
    def setValue(self, setTo):
        debugOut("TrackedState setValue")
        self.val = setTo
        return True
        
        
class AuthStorage:
    pass

class AuthValidator:
    def __init__(self, storage):
        self._store = storage
    

def setAuthValidator(val):
    debugOut("setAuthValidator()")
    
    
def tree():
    debugOut("tree()")
    return dict()

def top():
    debugOut("top()")
    return ItemContainer()

def print(msg):
    debugOut("print('%s')" % str(msg))
    
def println(msg):
    debugOut("println('%s')" % str(msg))
    
