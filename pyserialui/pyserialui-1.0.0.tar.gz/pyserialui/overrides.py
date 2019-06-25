'''
SerialUI basic overrides.  

@summary: Builds on the wrappers extensions to demonstrate how to override callbacks in classes, for various types
@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

'''

import SerialUI
import logging
import time
import pyserialui.wrappers as wrappers

log = logging.getLogger(__name__)

class Input(wrappers.Input):
    '''Use this class as a base for overrides of 
       SerialUI input request fields.
       
        class SomeInput(overrides.Input):
            
            def changed(self):
                reportstr = "OOOOOh the input changed to %s" % self.value()
                # do whatever you need to do with this value
                SerialUI.println(reportstr)
       
       Then, in your SerialUIHandler init (called once the menu 
       tree has been set up), you need only hold onto a reference to
       an instance of the class--bound to the correct input:
          # ...
          self.someinput = SomeInput(SerialUI.tree()['TheNameIGaveIt'])
       and that input's changed() method will be called whenever the 
       user actually changes the value using druid/serial terminal.
    '''
    def __init__(self, suiInputObject:SerialUI.Input):
        super().__init__(suiInputObject)
        
    def changed(self):
        ''' 
            @summary: changed() -- called whenever this value is modified.
        '''
        outstr = 'Input %s has changed to %s' % (
            self.key,
            str(self.value())
        )
        log.info(outstr) # local logging
        SerialUI.println(outstr) # remote notification
        
        
    def isValid(self, val):
        ''' 
            @summary: isValid(VALUE) -- called whenever this value is ABOUT TO BE modified.
            @return: True if we should accept it, False otherwise
        '''
        outstr = 'Input %s is requesting if "%s" is valid. Saying YES!' % (
            self.key,
            str(val)
        )
        print(outstr)
        return True
    


class Command(wrappers.Command):
    '''Use this class as a base for overrides of 
       SerialUI commands.
       
        class SomeCommand(overrides.Command):
            
            def triggered(self):
                reportstr = "Aaah command %s was triggered" % self.key
                # do whatever you need to do when the user triggers 
                SerialUI.println(reportstr)
       
       Then, in your SerialUIHandler init (called once the menu 
       tree has been set up), you need only hold onto a reference to
       an instance of the class--bound to the correct command:
          # ...
          self.somecommand = SomeCommand(SerialUI.tree()['TheCommandInQuestion'])
       and that command's triggered() method will be called whenever the 
       user actually issues the command.
    '''
    def __init__(self, suiCmdObject:SerialUI.Command):
        super().__init__(suiCmdObject)
        
    def triggered(self):
        outstr = 'Command %s triggered' % self.key
        print(outstr)
        log.info(outstr) # local logging
        SerialUI.println(outstr) # remote notification


class AuthStorage(SerialUI.AuthStorage):
    '''Sample AuthStorage override.  Use this class, 
       or SerialUI.AuthStorage, as your base class and 
       override the passphrase/setPassphrase/configured
       methods as required to actually implement.
       
       If you use this class without overriding, 
       the password stored will be 'secret' (or whatever 
       you passed as an argument to the constructor).
    '''
    def __init__(self, password:str='secret'):
        super().__init__()
        self.password = password
        
        
    def configured(self, forLevel:int):
        '''
            configured(ATLEVEL)
            @summary: used to query whether passphrase is set for given level
            @return: True if already set-up, False otherwise
        '''
        print('Requesting if configured() for level %i -- yes!' % forLevel)
        return True
        
    def passphrase(self, forLevel:int):
        '''
            passphrase(FORLEVEL)
            @summary: get passphrase stored for given level
            @return: passphrase string, or None
        '''
        print("Returning passphrase for level %i\n\n" % forLevel)
        return self.password
    def setPassphrase(self, setTo:str, forLevel:int):
        '''
            setPassphrase(SETTO:str, FORLEVEL)
            @summary: request to set the passphrase for given level
            @return: True if allowed and successful, False otherwise
        '''
        print('Request to setPassphrase (%s) for level %i -- failing' % 
              (str(setTo), forLevel) )
        return False
    
class AuthValidator(SerialUI.AuthValidator):
    '''
        Sample Authentication validator class.
        @summary: issues challenges and grants access to system
        @attention: the validators need a storage back-end, something 
        derived from SerialUI.AuthStorage, or AuthStorage above.
        
        The validator's job is to issue challenges, decode responses
        and grant (or deny) access.
        
        This will be done by overriding any or all of the three
        methods below: challenge/grantAccess/communicationType.
        
        
        To use it, keep a reference to the validator (and hence storage), and use
        setAuthValidator() whenever you wish to activate the authentication mechanism, 
        e.g. in the SerialUIHandler init:
            # ...
            self.validator = AuthValidator(AuthStorage())
            # set the validator:
            SerialUI.setAuthValidator(self.validator)
        
    '''
    Level_NoAccess=0
    Level_Guest=1
    Level_User=2
    Level_Admin=3
    
    Encoding_Plain=0
    Encoding_MD5=1
    Encoding_SHA256=2
    
    def __init__(self, storageObj:SerialUI.AuthStorage):
        super().__init__(storageObj)
        self.storage = storageObj
    
    def challenge(self, forLevel:int):
        '''
            challenge(FORLEVEL)
            @summary: request for an auth challenge at given level
            @return: challenge, as a string, or None if none required.
            @attention: If you care about levels, you may want to make note of the level 
            for which this challenge was issued (for use in grantAccess() below)
        '''
        print("Returning no challenge\n\n")
        return None
    
    def grantAccess(self, challengeResponse:str):
        '''
            grantAccess(CHALLENGERESPONSE)
            @summary: attempt to gain access, with challenge response
            @return: an access level (int).  Level_NoAccess (0) on failure, one of the other
            levels on success.
        '''
        print('Request to grantAccess (challenge response: %s)\n\n' %  str(challengeResponse) )
        levels = [self.Level_Guest, 
                  self.Level_User, 
                  self.Level_Admin]
        for aLev in levels:
            storedPass = self.storage.passphrase(aLev)
            if storedPass is not None and challengeResponse == storedPass:
                return aLev
        
        return self.Level_NoAccess
    
    def communicationType(self):
        '''    
            communicationType()
            @summary: how challenges will be interpreted, how responses will be transmitted.
            @return: one of the Encoding_* values: 0 for Encoding_Plain, etc.
            
            Encoding_Plain is basically a request for a password, which will be transmitted 
            to us in the grantAccess request.  Other encodings (still planned, at this stage) will
            use distinct mechanism (e.g. an expiring token returned as a challenge, and a hash
            of the token and shared secret sent to grantAccess())
        '''
        print('\n\n\nRequesting if comm type -- plain\n\n')
        return self.Encoding_Plain
    

