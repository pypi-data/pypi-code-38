import json
import os
import datetime
from squirreldb.persistence.persistence import Persistence
from squirreldb.persistence.storageState import StorageState
class JsonPersistence(Persistence):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.filePath = ""
        self.timeofupdation = ""
        self.timeofcreation = ""
    """
        Loads database dump stored in file into inMemory datastore. 
        Always loads any key that's not there in current InMemory datastore.
        If updatePolicy is to STALE, any key value in inMemoryDatastore is updated with Stored file data. 
        On INMEMORY updatePolicy, any data in InMemory is given higher preference.
        
        A User can call load either at start of his API interaction or Inbetween his inter-actions.
    """
    def load(self, databaseFilePath, inMemoryReference, updatePolicy=StorageState.INMEMORY):
        if databaseFilePath == None or inMemoryReference == None:
            return False
        try:
            with open(databaseFilePath, "r") as databaseFile:
                tempReference = json.load(databaseFile)
                for key in tempReference:
                    if key in inMemoryReference and updatePolicy == StorageState.STALE:
                        inMemoryReference[key] = tempReference[key]
                    if key not in inMemoryReference:
                        inMemoryReference[key] = tempReference[key]
        except FileNotFoundError:
            print("Information: Database file not found, init empty database")
            if updatePolicy == StorageState.STALE:
                inMemoryReference.clear()
            return  True
        except ValueError:
            print("Error: , Database file corrupt / in-unreadable format")
            return  False
        return True

    """
        Creates Store file, serializes any data in inMemoryStore and writes it off to given file path. 
        If file already exists, this operation basically overwrites the stale data. So caution must be taken if the existing store file may be required
        for future audit.
    """

    def store(self, inMemoryReference, databaseFilePath):
        if inMemoryReference == None or databaseFilePath == None:
            return False
        try:
            databaseFileExists = os.path.isfile(databaseFilePath)
            databaseDumpFile = open(databaseFilePath, "w")
            if databaseFileExists:
                databaseDumpFile.truncate(0)
            else:
                self.timeofcreation = datetime.datetime.now()
            self.timeofupdation = datetime.datetime.now()
            json.dump(inMemoryReference, databaseDumpFile)
        except Exception:
            print("Value Error in storing data ")
            return False
        return True

    def close(self):
        self.timeofcreation = ""
        self.timeofupdation = ""
        self.filename =""
        self.filePath = ""
        return True


