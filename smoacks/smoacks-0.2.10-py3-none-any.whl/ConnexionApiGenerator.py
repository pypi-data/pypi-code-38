# ConnexionApiGenerator.py - Creates an object implementing a Connexion API
import os
from jinja2 import Environment, Template, FileSystemLoader
from smoacks.sconfig import sconfig

class ConnexionApiGenerator:
    def __init__(self, app_object):
        self._app_object = app_object
        self.name = self._app_object.name

    def getJinjaDict(self):
        # Establish constant values and the overall dictionary structure
        result = {
            'name': self.name,
            'idList': None,
            'pkList': None,
            'idCount': self._app_object._idCount,
            'hasSearch': False
        }
        # Loop through the properties and update the structure where needed
        properties = self._app_object.getAllProperties()
        for prop in properties:
            if prop.isId:
                result['name_id'] = prop.name
                if not result['idList']:
                    result['idList'] = prop.name
                    result['pkList'] = self.name + '.' + prop.name
                else:
                    result['idList'] += ', ' + prop.name
                    result['pkList'] += ', ' + self.name + '.' + prop.name
            if prop.searchField:
                result['hasSearch'] = True
                result['search_field'] = prop.name
        result.update(sconfig['env_defaults'])
        return result

    def render(self):
        env = Environment(
            loader = FileSystemLoader('templates')
        )
        template = env.get_template('ConnexionAPIs.jinja')
        filedir = os.path.join(sconfig['structure']['root'], sconfig['structure']['apiobjectdir'])
        if not os.path.isdir(filedir):
            os.makedirs(filedir, exist_ok=True)
        outfilename = os.path.join(filedir, "{}s.py".format(self._app_object.getSnakeName()))
        if not os.path.isfile(outfilename):
            outfile = open(outfilename, "w")
            outfile.write(template.render(self.getJinjaDict()))
            outfile.close()
