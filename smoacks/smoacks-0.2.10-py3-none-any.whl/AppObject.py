# AppObject.py - Application objects
from smoacks.util import to_camelcase, to_mixedcase, to_snakecase

scr_objects = dict()

class AppObject:
    def __init__(self, name, desc = None):
        self.name = name
        self.description = desc if desc else name
        self._schemas = []
        self._properties = []
        self._paramVerbs = {}
        self._respVerbs = {}
        self._idCount = 0
        self._idProperty = None
        self.hasSearch = False
        self.identitySchemaName = None
        self.extendedSchemaName = None
        self.emitTestData = False
        self.rbacControlled = None
        self.relationships = None
        self.searchField = None
    
    def addSchema(self, schema):
        self._schemas.append(schema)
        if schema.identityObject and not self.identitySchemaName:
            self.identitySchemaName = schema.name
            self.rbacControlled = schema.rbacControlled
            if schema.relationships:
                self.relationships = schema.relationships
            for prop in schema.getProperties().values():
                self._properties.append(prop)
                if prop.isId:
                    self._idProperty = prop
                    self._idCount += 1
                if prop.searchField:
                    self.hasSearch = True
                    self.searchField = prop.name
        if schema.extendedObject:
            self.extendedSchemaName = schema.name

    def addParamVerb(self, schema):
        self._paramVerbs[schema.paramVerb] = schema.name

    def addRespVerb(self, schema):
        self._respVerbs[schema.respVerb] = schema.name

    def getSnakeName(self):
        return to_snakecase(self.name)

    def getRbacController(self):
        if self.rbacControlled:
            return to_snakecase(self.rbacControlled)
        else:
            return None
    
    def getCamelName(self):
        return to_camelcase(self.name)
    
    def getMixedName(self):
        return to_mixedcase(self.name)

    def getCreateObject(self):
        # Loop through the properties and update the structure where needed
        result = {}
        for prop in self._properties:
            if (not prop.isId or self._idCount > 1) and not prop.readOnly:
                result[prop.name] = prop.example
        return result

    def getAllProperties(self):
        return self._properties
