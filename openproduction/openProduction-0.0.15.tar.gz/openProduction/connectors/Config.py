from openProduction.common import Types

class Config:
    def __init__(self, description):
        #description must be a list of Types.BaseType
        if type(description) != type([]):
            raise RuntimeError("description must by a list")
            
        for e in description:
            if not isinstance(e, Types.BaseType):
                raise RuntimeError("each entry of description must be a subclass of Types.BaseType")
        
        self.__fields__ = description
        self._curIdx = 0
        self.isZombie = False
        self.err = ""
           
    def __next__(self):
        if self._curIdx >= len(self.__fields__):
            raise StopIteration()
        else:
            rv = self.__fields__[self._curIdx]
            self._curIdx += 1
            return rv
    
    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self.__fields__)
    
    def fromDict(self, myDict):
        ok = True
        fieldNames = []
        for field in self.__fields__:
            fieldNames.append(field.name)
        
        dictKeys = []
        for key, val in myDict.items():
            dictKeys.append(key)
           
        missingKeys = set(fieldNames) - set(dictKeys)
             
        if len(missingKeys) > 0:
            self.err = "missing keys: "+str(missingKeys)
            ok = False
            
        if ok:
            for field in self.__fields__:
                field.value = myDict[field.name]
            
        return ok
        
    def __getitem__(self, key):
        for field in self.__fields__:
            if field.name == key:
                return field.value
    
    def errmsg(self):
        return self.err