# NoseTestGenerator.py - Creates nose tests for a model API
import os
from jinja2 import Environment, Template, FileSystemLoader
from smoacks.sconfig import sconfig
from smoacks.AppObject import scr_objects

class NoseTestGenerator:
    def __init__(self, app_object):
        self._app_object = app_object
        self.name = self._app_object.name

    def getJinjaDict(self):
        # Establish constant values and the overall dictionary structure
        result = {
            'app_name': sconfig['env_defaults']['smoacks_app_name'],
            'name': self.name,
            'hasSearch': False,
            'idCount': self._app_object._idCount,
            'smoacks_unit_test_default_role': sconfig['env_defaults']['smoacks_unit_test_default_role'],
            'idsString': None,
            'snakeName': self._app_object.getSnakeName(),
            'createObj': self._app_object.getCreateObject(),
            'foreignKeys': []
        }
        properties = self._app_object.getAllProperties()
        getAsserts = []
        createAssignments = []
        unitTestEditObject = {}
        id_list = []
        unitTestAssert = None
        for prop in properties:
            if prop.searchField:
                result['hasSearch'] = True
            if prop.foreignKey:
                fk_app_object = scr_objects[prop.foreignKey]
                fk_result = {
                    'name': prop.name,
                    'mixedName': prop.foreignKey,
                    'createObj': fk_app_object.getCreateObject(),
                    'snakeName': fk_app_object.getSnakeName(),
                    'idField': fk_app_object._idProperty.name
                }
                if fk_app_object.rbacControlled and fk_app_object.rbacControlled != self.name:
                    fk_result['rbacControlled'] = fk_app_object.rbacControlled
                result['foreignKeys'].append(fk_result)
            if prop.isId:
                result['name_id'] = prop.name
                id_list.append(prop.name)
                if not prop.readOnly and prop.example != None and not prop.foreignKey:
                    createAssignments.append('test_obj.{} = {}'.format(prop.name, prop.getExamplePythonLiteral()))
            # We need to change a value in unit tests of PUT verb
            elif prop.example != None and not prop.readOnly:
                createAssignments.append('test_obj.{} = {}'.format(prop.name, prop.getExamplePythonLiteral()))
                if prop.editUnitTest:
                    unitTestEditObject[prop.name] = prop.editUnitTest
                    result['editUnitTestAssignment'] = 'added_obj.{} = {}'.format(prop.name, prop.getUnitTestLiteral())
                    unitTestAssert = 'assert resp.{} == added_obj.{}'.format(prop.name, prop.name)
                    getAsserts.append('assert resp.{} == {}'.format(prop.name, prop.getExamplePythonLiteral()))
                else:
                    unitTestEditObject[prop.name] = prop.example
                    if prop.foreignKey:
                        fk_app_object = scr_objects[prop.foreignKey]
                        getAsserts.append('assert resp.{} == added_{}.{}'.format(prop.name, fk_app_object.getSnakeName(), prop.name))
                    else:
                        getAsserts.append('assert resp.{} == {}'.format(prop.name, prop.getExamplePythonLiteral()))
        if len(id_list) == 1:
            result['idsString'] = 'added_obj.{}'.format(id_list[0])
        else:
            result['idsString'] = '[added_obj.' + ', added_obj.'.join(id_list) + ']'
        result['getAsserts'] = getAsserts
        result['createAssignments'] = createAssignments
        result['unitTestEditObject'] = str(unitTestEditObject)
        result['unitTestAssert'] = unitTestAssert
        return result

    def render(self):
        env = Environment(
            loader = FileSystemLoader('templates')
        )
        template = env.get_template('NoseTests.jinja')
        filedir = os.path.join(sconfig['structure']['root'], sconfig['structure']['testdir'])
        if not os.path.isdir(filedir):
            os.makedirs(filedir, exist_ok=True)
        outfile = open(os.path.join(filedir, "test-{}-api.py".format(self._app_object.getSnakeName())), "w")
        outfile.write(template.render(self.getJinjaDict()))
