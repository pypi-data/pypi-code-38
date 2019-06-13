# Schema.py - Tools for understanding OpenAPI 3.0 schema definitions
from smoacks.Property import Property

scr_schemas = dict()

# This handles a subset of the OpenAPI schema specification.
# It is intended to include the core components of the specification
# that are suitable for direct persistence into a SQL-based database
# Specifically, it can handle a top-level typed object that is defined
# with a property  list, or a property list combined with another
# schema reference via allOf
class Schema:

    def __init__(self, name, schemaYaml):
        self.name = name
        self._yaml = schemaYaml
        self._properties = dict()
        self._references = []
        self.description = self._yaml['description'] if 'description' in self._yaml else None
        self.identityObject = self._yaml['x-smoacks-create'] if 'x-smoacks-create' in self._yaml else None
        self.extendedObject = self._yaml['x-smoacks-extended'] if 'x-smoacks-extended' in self._yaml else None
        self.updateObject = self._yaml['x-smoacks-update'] if 'x-smoacks-update' in self._yaml else None
        self.appObject = self._yaml['x-smoacks-object'] if 'x-smoacks-object' in self._yaml else None
        self.paramVerb = self._yaml['x-smoacks-api-verb-param'] if 'x-smoacks-api-verb-param' in self._yaml else None
        self.rbacControlled = self._yaml['x-smoacks-rbac-controlled'] if 'x-smoacks-rbac-controlled' in self._yaml else None
        self.respVerb = self._yaml['x-smoacks-api-verb-resp'] if 'x-smoacks-api-verb-resp' in self._yaml else None
        self.emitTestData = self._yaml['x-smoacks-test-data'] if 'x-smoacks-test-data' in self._yaml else True
        self.relationships = self._yaml['x-smoacks-relationships'] if 'x-smoacks-relationships' in self._yaml else None
        propertiesYaml = None
        if 'properties' in self._yaml:
            propertiesYaml = self._yaml['properties']
        elif 'allOf' in self._yaml:
            allOf = self._yaml['allOf']
            for item in allOf:
                if 'type' in item and item['type'] == 'object':
                    propertiesYaml = item['properties']
                elif '$ref' in item:
                    self._references.append(item['$ref'])
        if propertiesYaml is not None:
            for propertyName in propertiesYaml:
                self._properties[propertyName] = Property(self.name, propertyName, propertiesYaml[propertyName])

    # Allow contents to be printed when casting to string
    def __str__(self):
        return str(self.__dict__)

    def getProperties(self):
        result = self._properties.copy()
        for ref in self._references:
            pieces = ref.split('/')
            ref_schema_name = pieces[-1]
            print('Found ref_schema_name: {}'.format(ref_schema_name))
            result.update(scr_schemas[ref_schema_name].getProperties())
        return result

    def getProperty(self, propertyName):
        return self._properties[propertyName]
