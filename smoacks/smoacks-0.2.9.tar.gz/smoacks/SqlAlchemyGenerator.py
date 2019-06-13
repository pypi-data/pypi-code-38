# CreateApiGenerator.py - Creates an object representing a create API
import os
from jinja2 import Environment, Template, FileSystemLoader
from smoacks.sconfig import sconfig
from smoacks.AppObject import scr_objects

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
            'app_name': sconfig['env_defaults']['smoacks_app_name'],
            'app_prefix': sconfig['env_defaults']['smoacks_app_api_prefix'],
            'name': self.name,
            'snakeName': self._app_object.getSnakeName(),
            'mixedName': self.name,
            'search_field': None,
            'hasSearch': False,
            'dmFields': [],
            'genprefix': sconfig['structure']['genprefix'],
            'gensubdir': sconfig['structure']['gensubdir'],
            'idCount': self._app_object._idCount,
            'relationships': [],
            'fields': [],
            'write_fields': [],
            'rbacControlled': False,
            'uuid_set': set(),
            'fkey_imports': []
        }
        # If app object is rbac controlled, set values needed for client APIs
        if self._app_object.rbacControlled:
            result['rbacControlled'] = True
            result['rbacClass'] = self._app_object.rbacControlled
        # Loop through the properties and update the structure where needed
        read_only_fields = []
        id_fields = []
        properties = self._app_object.getAllProperties()
        for prop in properties:
            result['fields'].append(prop.name)
            if prop.readOnly:
                read_only_fields.append(prop.name)
            else:
                if not prop.foreignKey:
                    result['write_fields'].append(prop.name)
                else:
                    # We need to know the table name, and the search field for that table
                    fk_table_name = prop.foreignKey
                    fk_ao = scr_objects[fk_table_name]
                    fk_search_field = fk_ao.searchField
                    result['write_fields'].append('{}.{}'.format(fk_table_name, fk_search_field))
                    result['fkey_imports'].append({'table': fk_table_name, 'search_field': fk_search_field, 'fkey_field': prop.name})
            if prop.searchField:
                result['search_field'] = prop.name
                result['hasSearch'] = True
            if prop.isId:
                id_fields.append(prop.name)
                result['name_id'] = prop.name
                result['dmFields'].append(self.getField(prop))
                result['uuid_set'].add(prop.name)
            if not prop.isId and not (prop.name in {'record_created', 'record_updated'}):
                result['dmFields'].append(self.getField(prop))
                if prop.format == 'uuid':
                    result['uuid_set'].add(prop.name)
        result['ro_fields'] = "{'" + "', '".join(read_only_fields) + "'}" if len(read_only_fields) > 0 else 'set()'
        result['id_fields'] = "{'" + "', '".join(id_fields) + "'}" if len(id_fields) > 1 else "'{}'".format(id_fields[0])
        result['get_ids'] = "self." + ", self.".join(id_fields)
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
        jinja_dict = self.getJinjaDict()

        # Render generated data model objects
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
        outfile.write(template.render(jinja_dict))
        outfile.close()

        # Render data model customization objects (if needed)
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
            of2.write(template2.render(jinja_dict))
            of2.close()

        # Render API client objects
        clientdir = os.path.join(sconfig['structure']['root'],
                                 sconfig['env_defaults']['smoacks_app_name'])
        if not os.path.isdir(clientdir):
            os.makedirs(clientdir, exist_ok=True)
        module_filename3 = os.path.join(clientdir, "__init__.py")
        if not os.path.isfile(module_filename3):
            initfile3 = open(module_filename3, "w")
            initfile3.close()
        co_filename = os.path.join(clientdir, "{}.py".format(self.name))
        co_template = env.get_template('ClientApi.jinja')
        co_file = open(co_filename, "w")
        co_file.write(co_template.render(jinja_dict))
        co_file.close()

        # Render Add CLI object directory
        clidir = os.path.join(sconfig['structure']['root'],
                              sconfig['env_defaults']['smoacks_app_name'],
                              sconfig['structure']['clisubdir'])
        if not os.path.isdir(clidir):
            os.makedirs(clidir, exist_ok=True)
        module_filename4 = os.path.join(clidir, "__init__.py")
        if not os.path.isfile(module_filename4):
            initfile4 = open(module_filename4, "w")
            initfile4.close()
        
        # Add modules
        add_cli_filename = os.path.join(clidir, "add_{}.py".format(self._app_object.getSnakeName()))
        if not os.path.isfile(add_cli_filename):
            add_cli_template = env.get_template('cli_add.jinja')
            add_cli = open(add_cli_filename, "w")
            add_cli.write(add_cli_template.render(jinja_dict))
            add_cli.close()

        # Import modules
        imp_cli_filename = os.path.join(clidir, "imp_{}.py".format(self._app_object.getSnakeName()))
        if not os.path.isfile(imp_cli_filename):
            imp_cli_template = env.get_template('cli_import.jinja')
            imp_cli = open(imp_cli_filename, "w")
            imp_cli.write(imp_cli_template.render(jinja_dict))
            imp_cli.close()

        # Search modules
        if jinja_dict['hasSearch']:
            search_cli_filename = os.path.join(clidir, "search_{}.py".format(self._app_object.getSnakeName()))
            if not os.path.isfile(search_cli_filename):
                search_cli_template = env.get_template('cli_search.jinja')
                search_cli = open(search_cli_filename, "w")
                search_cli.write(search_cli_template.render(jinja_dict))
                search_cli.close()
