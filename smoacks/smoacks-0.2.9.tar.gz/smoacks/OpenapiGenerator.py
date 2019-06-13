# CreateApiGenerator.py - Creates an object representing a create API
import os
from jinja2 import Environment, Template, FileSystemLoader
import yaml
from smoacks.sconfig import sconfig
from smoacks.Schema import scr_schemas

class OpenapiGenerator:
    def __init__(self, app_object):
        self._app_object = app_object
        self.name = self._app_object.name

    def getJinjaDict(self):
        # Establish constant values and the overall dictionary structure
        ao = self._app_object
        result = {
            'name': self.name,
            'idList': [],
            'snakeName': self._app_object.getSnakeName(),
            'mixedName': self.name,
            'identitySchemaName': self._app_object.identitySchemaName,
            'extendedSchemaName': self._app_object.extendedSchemaName,
            'hasSearch': False,
            'paramVerbSchema': {
                'post': ao._paramVerbs['post'] if 'post' in ao._paramVerbs else ao.identitySchemaName,
                'search': 'schemas/{}'.format(ao._paramVerbs['search']) if 'search' in ao._paramVerbs else 'parameters/search_text',
                'getVerb': ao._paramVerbs['get'] if 'get' in ao._paramVerbs else ao.identitySchemaName,
                'put': ao._paramVerbs['put'] if 'put' in ao._paramVerbs else ao.identitySchemaName
            },
            'respVerbSchema': {
                'search': ao._respVerbs['search'] if 'search' in ao._respVerbs else ao.identitySchemaName,
                'getVerb': ao._respVerbs['get'] if 'get' in ao._respVerbs else ao.identitySchemaName
            },
        }
        result.update(sconfig['env_defaults'])
        # Loop through the properties and update the structure where needed
        properties = self._app_object.getAllProperties()
        for prop in properties:
            if prop.isId:
                result['name_id'] = prop.name
                result['idList'].append(prop.name)
            if prop.searchField:
                result['hasSearch'] = True
        return result

    def render_to_yaml_obj(self):
        env = Environment(
            loader = FileSystemLoader('templates')
        )
        template = env.get_template('ModelAPIs.jinja')
        rendered_string = template.render(self.getJinjaDict())
#        print('rendered_string = ', rendered_string)
        result = yaml.load(rendered_string, Loader=yaml.FullLoader)
        return result
