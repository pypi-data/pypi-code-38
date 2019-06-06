import json
import string
from awscli.customizations.cloudformation.yamlhelper import yaml_parse


class CfnTemplate(string.Template):
    delimiter = '$'
    idpattern = r'[a-z][\w\,\+\=\:\-\.\x2f\x5c\*\(\)\[\]\x7c]*'


class DynamoDBResource:
    def __init__(self, resource):
        self.resource = resource

    def tableName(self):
        return self.resource['Properties']['TableName']

    def properties(self):
        return self.resource['Properties']


class CFNParser:
    def __init__(self, filename, parameters):
        self.parameters = parameters
        self.template = self.__load_yaml(filename)
        self.resources = self.template['Resources']

    def all_dynamodb_tables(self):
        for key in self.resources.keys():
            resource = self.resources[key]
            if resource['Type'] == 'AWS::DynamoDB::Table':
                self.__resolve_parameters(resource)
                yield DynamoDBResource(resource)

    def __load_yaml(self, filename):
        with open(filename) as f:
            return yaml_parse(f.read())

    def __resolve_parameters(self, node):
        for key in node:
            val = node[key]
            if isinstance(val, dict) and len(val) == 1 and next(iter(val)) == 'Fn::Sub':
                node[key] = CfnTemplate(
                    val['Fn::Sub']).safe_substitute(self.parameters)
            elif isinstance(val, dict):
                self.__resolve_parameters(val)
