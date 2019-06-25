'''
sqliteauth 

@summary: Authentication storage/validator based on an SQLite3 back-end.
@author: Pat Deegan
@copyright: Copyright (C) 2019 Pat Deegan, https://psychogenic.com

@attention: this is sample code, passwords are stored in cleartext in the db.

To use it, keep a reference to the validator (and hence storage) whenever you 
wish to activate the authentication mechanism, e.g. in the SerialUIHandler init:
    # ...
    self.validator = sqliteauth.AuthValidator(sqliteauth.AuthStorage('/path/to/mypass.db'))
    # set the validator:
    SerialUI.setAuthValidator(self.validator)

'''
import pyserialui.overrides as overrides
import sqlite3


class AuthStorage(overrides.AuthStorage):
    '''
        Authentication storage that sticks passwords in rows 
        of a 'users' table, within an sqlite3 db file.
        
        Must be constructed by passing the full path to the 
        persistent db file:
          mystorage = sqliteauth.AuthStorage('/path/to/passwords.db')
        
    '''
    RowNames = {
        '1': 'Guest',
        '2': 'User',
        '3': 'Admin'
    }
    def __init__(self, path_to_db:str):
        super().__init__();
        self.db_path = path_to_db
        self._dbconn = None
    
    
    
    def passphrase(self, forLevel:int):
        print("Getting passphrase for level %i" % forLevel)
        entry = self.getEntryForLevel(forLevel)
        if entry is None or not len(entry):
            # this shouldn't be called, if there isn't 
            # a password configured... 
            print("nothing set for level %i??" % forLevel)
            return 'AAAAGH'
        
        print("Returning pass from entry %s " % str(entry))
        return entry[2]
    
        
    
    def setPassphrase(self, setTo:str, forLevel:int):
        entry = self.getEntryForLevel(forLevel)
        cursor = self.getDBCursor()
        if cursor is None:
            return False
        nm = 'Unknown'
        if str(forLevel) in self.RowNames:
            nm = self.RowNames[str(forLevel)]
            
        print("Setting pass for level %s (%i)" % (nm, forLevel))
        if entry is None or not len(entry):
            print("First time, creating entry")
            # nothing set yet
            cursor.execute("INSERT into users VALUES('%s', %i, '%s')" % 
                           (nm, forLevel, setTo))
        else:
            print("Existing entry, updating")
            
            cursor.execute("UPDATE users set pass='%s' where level=%i" %(
                    setTo, forLevel
                ))
        
        self.commitChanges()
            
    
    
    def configured(self, forLevel:int):
        print("Checking if level %i is configured..." % forLevel)
        entry = self.getEntryForLevel(forLevel)
        if entry is None:
            print("No, not configured yet")
            return False
        
        print("Yes, already have entry %s" % str(entry))
        return True
    
    def getEntryForLevel(self, lev:int):
        cursor = self.getDBCursor()
        if not cursor:
            return None
        
        cursor.execute("SELECT * from users WHERE level='%i';" % lev)
        res = cursor.fetchall()
        if res is None or not len(res):
            return None
        return res[0]
    
    def initDB(self, dbconn):
        cursor = dbconn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        vals = cursor.fetchall()
        if vals is None or not len(vals):
            cursor.execute('''CREATE TABLE users
                                 (type text, level int, pass text)''')
            dbconn.commit()
    
        
    def getDB(self):
        if self._dbconn is not None:
            return self._dbconn
        
        self._dbconn = sqlite3.connect(self.db_path)
        self.initDB(self._dbconn)
        return self._dbconn
    
    def getDBCursor(self):
        db = self.getDB()
        if db:
            return db.cursor()
        return None
    def commitChanges(self):
        if self._dbconn is None:
            return False
        
        self._dbconn.commit()
        return True
        
    def closeDB(self, autoCommit=True):
        if autoCommit:
            if not self.commitChanges():
                return False
        
        self.getDB().close()



class AuthValidator(overrides.AuthValidator):
    
    def grantAccess(self, challengeResponse:str):
        levels = [self.Level_Guest, 
                  self.Level_User, 
                  self.Level_Admin]
        for aLev in levels:
            apass = self.storage.passphrase(aLev)
            if apass is not None and apass == challengeResponse:
                return aLev
        
        return 0
    