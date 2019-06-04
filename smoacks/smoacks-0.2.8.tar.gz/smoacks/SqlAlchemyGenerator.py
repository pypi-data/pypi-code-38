# CreateApiGenerator.py - Creates an object representing a create API
import os
from jinja2 import Environment, Template, FileSystemLoader
from smoacks.sconfig import sconfig

class SqlAlchemyGenerator:
    def __init__(self, app_object):
        self._app_object = app_object
        self.name = self._app_object.name

    def getField(self, prop):
        if prop.type == 'string':
            if prop.isId:
                fk_text = ", ForeignKey('{}.{}')".format(prop.foreignKey, prop.name) if prop.foreignKey else ""
                return "{} = Column(BINARY(16){}, primary_key=True)".format(prop.name, fk_text)
            elif prop.format == 'date':
                return "{} = Column(DateTime)".format(prop.name)
            elif prop.format == 'uuid':
                fk_text = ", ForeignKey('{}.{}')".format(prop.foreignKey, prop.name) if prop.foreignKey else ""
                return "{} = Column(BINARY(16){})".format(prop.name, fk_text)
            elif prop.maxLength and prop.maxLength > 0:
                return "{} = Column(String({}))".format(prop.name, prop.maxLength)
            else:
                return "{} = Column(String(80))".format(prop.name)
        elif prop.type == 'number':
            if prop.format == 'double':
                return "{} = Column(Double)".format(prop.name)
            else:
                return "{} = Column(Float)".format(prop.name)
        elif prop.type == 'integer':
            if prop.format == 'int64':
                return "{} = Column(Long)".format(prop.name)
            else:
                return "{} = Column(Integer)".format(prop.name)
        elif prop.type == 'object':
            return "{} = Column(JSON)".format(prop.name)
        elif prop.type == 'boolean':
            return "{} = Column(Boolean)".format(prop.name)
        else:
            raise ValueError("Property {} has invalid type {}".format(prop.name, prop.type))

    def getJinjaDict(self):
        # Establish constant values and the overall dictionary structure
        result = {
            'name': self.name,
            'snakeName': self._app_object.getSnakeName(),
            'mixedName': self.name,
            'dmFields': [],
            'genprefix': sconfig['structure']['genprefix'],
            'gensubdir': sconfig['structure']['gensubdir'],
            'idCount': self._app_object._idCount,
            'relationships': [],
            'uuid_set': set()
        }
        # Loop through the properties and update the structure where needed
        properties = self._app_object.getAllProperties()
        for prop in properties:
            if prop.isId:
                result['name_id'] = prop.name
                result['dmFields'].append(self.getField(prop))
                result['uuid_set'].add(prop.name)
            if not prop.isId and not (prop.name in ['record_created', 'record_updated']):
                result['dmFields'].append(self.getField(prop))
                if prop.format == 'uuid':
                    result['uuid_set'].add(prop.name)
        # Loop through relationships
        for rel in self._app_object.relationships:
            ao_rel = self._app_object.relationships[rel]
            rel_data = {
              'name': rel,
              'table': ao_rel['table'],
              'field': ao_rel['field']
            }
            if 'cascade' in ao_rel:
                print('---> cascading {} for {} on {}'.format(ao_rel['cascade'], rel, self._app_object.name))
                rel_data['cascade'] = ao_rel['cascade']
            result['relationships'].append(rel_data)
        return result

    def render(self):
        env = Environment(
            loader = FileSystemLoader('templates')
        )
        template = env.get_template('SQLAlchemyModel.jinja')
        gendir = os.path.join(sconfig['structure']['root'],
                              sconfig['structure']['datamodeldir'],
                              sconfig['structure']['gensubdir'])
        if not os.path.isdir(gendir):
            os.makedirs(gendir, exist_ok=True)
        module_filename = os.path.join(gendir, "__init__.py")
        if not os.path.isfile(module_filename):
            initfile = open(module_filename, "w")
            initfile.close()
        outfile = open(os.path.join(gendir, "{}{}.py".format(sconfig['structure']['genprefix'], self.name)), "w")
        outfile.write(template.render(self.getJinjaDict()))
        outfile.close()
        filedir = os.path.join(sconfig['structure']['root'],
                               sconfig['structure']['datamodeldir'])
        module_filename2 = os.path.join(gendir, "__init__.py")
        if not os.path.isfile(module_filename2):
            initfile2 = open(module_filename2, "w")
            initfile2.close()
        # We should not overwrite customization file if it exists
        dmo_filename = os.path.join(filedir, "{}.py".format(self.name))
        if not os.path.isfile(dmo_filename):
            template2 = env.get_template('DataModelObject.jinja')
            of2 = open(dmo_filename, "w")
            of2.write(template2.render(self.getJinjaDict()))
            of2.close()
