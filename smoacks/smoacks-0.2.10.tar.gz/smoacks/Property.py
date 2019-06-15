# Property.py - Handles OpenAPI 3.0 properties, with extended smoacks attributes
import json
from smoacks.util import to_camelcase, to_mixedcase, to_snakecase

# This handles a subset of the OpenAPI properties specification.
# It is intended to include the core components of the specification
# that are suitable for direct persistence into a SQL-based database
class Property:
    def __init__(self, schemaName, name, propertyYaml):
        self.schemaName = schemaName
        self.name = name
        self._yaml = propertyYaml
        if 'type' in propertyYaml:
            self.type = propertyYaml['type']
            self.baseObject = propertyYaml['x-smoacks-base-object'] if 'x-smoacks-base-object' in propertyYaml else False
            self.createOnly = propertyYaml['x-smoacks-create-only'] if 'x-smoacks-create-only' in propertyYaml else False
            self.description = propertyYaml['description'] if 'description' in propertyYaml else None
            self.editUnitTest = propertyYaml['x-smoacks-edit-unit-test'] if 'x-smoacks-edit-unit-test' in propertyYaml else None
            self.enum = propertyYaml['enum'] if 'enum' in propertyYaml else None
            self.example = propertyYaml['example'] if 'example' in propertyYaml else None
            self.exclusiveMaximum = propertyYaml['exclusiveMaximum'] if 'exclusiveMaximum' in propertyYaml else False
            self.exclusiveMinimum = propertyYaml['exclusiveMinimum'] if 'exclusiveMinimum' in propertyYaml else False
            self.foreignKey = propertyYaml['x-smoacks-foreign-key'] if 'x-smoacks-foreign-key' in propertyYaml else None
            self.format = propertyYaml['format'] if 'format' in propertyYaml else None
            self.isId = propertyYaml['x-smoacks-model-id'] if 'x-smoacks-model-id' in propertyYaml else False
            self.maximum = propertyYaml['maximum'] if 'maximum' in propertyYaml else None
            self.maxLength = propertyYaml['maxLength'] if 'maxLength' in propertyYaml else None
            self.minimum = propertyYaml['minimum'] if 'minimum' in propertyYaml else None
            self.minLength = propertyYaml['minLength'] if 'minLength' in propertyYaml else None
            self.nullable = propertyYaml['nullable'] if 'nullable' in propertyYaml else False
            self.pattern = propertyYaml['pattern'] if 'pattern' in propertyYaml else None
            self.searchField = propertyYaml['x-smoacks-search-field'] if 'x-smoacks-search-field' in propertyYaml else False
            self.stringFormat = propertyYaml['format'] if 'format' in propertyYaml else None
            self.readOnly = propertyYaml['readOnly'] if 'readOnly' in propertyYaml else False
        elif '$ref' in propertyYaml:
            self.ref = propertyYaml['$ref']

    # ID is special cased in Redux Objects
    def getCamelName(self):
        if self.name != to_snakecase(self.schemaName) + "_id":
            return to_camelcase(self.name)
        else:
            return "id"

    # ID is special cased in Redux Objects
    def getMixedName(self):
        if self.name != to_snakecase(self.schemaName) + "_id":
            return to_mixedcase(self.name)
        else:
            return "Id"

    # ID is special cased in Redux Objects
    def getUpperName(self):
        if self.name != to_snakecase(self.schemaName) + "_id":
            return self.name.upper()
        else:
            return "ID"

    # Returns a string for what the default value of this property should be
    # assuming use only in JavaScript (Redux Object)
    def defaultValue(self):
        if self.type == 'string':
            if self.format == 'date':
                return "new Date(0)"
            else:
                return "''"
        elif self.type == 'date':
            return "new Date(0)"
        elif self.type == 'object':
            return "Map({})"
        else:
            return "0"

    # Gets example value in form suitable for JavaScript
    def getExampleJs(self):
        if self.type == 'string' and self.example:
            return "'" + self.example + "'"
        elif self.type == 'object' and self.example:
            return json.dumps(self.example)
        elif not self.example:
            return 'undefined'
        else:
            return self.example

    # Gets example value in form suitable for Python
    def getExamplePythonLiteral(self):
        if self.type == 'string' and self.example:
            return "'" + self.example + "'"
        elif self.type == 'object' and self.example:
            return json.dumps(self.example)
        elif self.example == None:
            return 'None'
        else:
            return self.example

    # Gets example value in form suitable for Python
    def getUnitTestLiteral(self):
        if self.type == 'string' and self.editUnitTest:
            return "'" + self.editUnitTest + "'"
        elif self.type == 'object' and self.editUnitTest:
            return json.dumps(self.editUnitTest)
        elif not self.editUnitTest:
            return 'None'
        else:
            return self.editUnitTest

    # Gets invalid value for validation tests
    def getInvalidValue(self):
        if self.type == 'string':
            if self.minLength:
                return "'X'"
            elif self.maxLength:
                return "'" + "x" * (self.maxLength+1) + "'"
            elif not self.nullable:
                return 'undefined'
            else:
                return 10
        elif self.type == 'object':
            return 'undefined'
        else:
            return 'undefined'

    # Gets true if this property should have clent validations
    def needsValidation(self):
        result = False
        if (self.readOnly):
            # Any readOnly property requires no client validation
            result = False
        elif self.maxLength or self.minLength or self.minimum or self.maximum or self.enum:
            result = True
        elif not result and not self.nullable:
            result = True
        elif self.pattern:
            result = True
        return result

    def needsInputTransform(self):
        result = False
        if (self.type == 'string' and self.format == 'date'):
            result = True
        return result

    def needsOutputTransform(self):
        result = False
        if (self.type == 'string' and self.format == 'date'):
            result = True
        if (self.type == 'object'):
            result = True
        return result

    # Allow contents to be printed when casting to string
    def __str__(self):
        return str(self.__dict__)


