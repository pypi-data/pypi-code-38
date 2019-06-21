class BaseType:
    def __init__(self, name, description):
        self.name = name
        if description == None:
            self.description = name
        else:
            self.description = description
        self.value = None
        
    def clear(self):
        self.value = None
        
    def __str__(self):
        return str(self.value)
            
    def setValue(self, value):
        self.value = value
        
    def getValue(self):
        return self.value
    
    def getName(self):
        return self.value

class Date(BaseType):
    def __init__(self, name, description, value=None):
        super(Date, self).__init__(name, description)
        self.value = value
        
class Path(BaseType):
    def __init__(self, name, description, value=None):
        super(Path, self).__init__(name, description)
        self.value = value
        
class String(BaseType):
    def __init__(self, name, description, value=None):
        super(String, self).__init__(name, description)
        self.value = value
        
class Int(BaseType):
    def __init__(self, name, description=None, value=None, minVal=None, maxVal=None):
        super(Int, self).__init__(name, description)
        self.value = value
        self.minVal = minVal
        self.maxVal = maxVal

class Float(BaseType):
    def __init__(self, name, description=None, value=None, minVal=None, maxVal=None):
        super(Float, self).__init__(name, description)
        self.value = value
        self.minVal = minVal
        self.maxVal = maxVal

class Bool(BaseType):
    def __init__(self, name, description=None, value=None):
        super(Bool, self).__init__(name, description)
        self.value = value

class Password(BaseType):
    def __init__(self, name, description, value=None):
        super(Password, self).__init__(name, description)
        self.value = value
        