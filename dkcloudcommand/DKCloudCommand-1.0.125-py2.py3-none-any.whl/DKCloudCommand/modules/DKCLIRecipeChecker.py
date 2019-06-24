import os
import json
import click

from DKFileHelper import DKFileHelper
from DKCommon.DKFileEncode import DKFileEncode
from DKRecipeDisk import IGNORED_FILES


class DKCLIRecipeChecker:

    EXCEPTION_MESSAGE_HEADER = 'DKCLIRecipeChecker: '
    MERGE_ISSUE_YOURS = '<<<<<<< your'
    MERGE_ISSUE_THEIR = '>>>>>>> their'
    NODE_TYPE_LIST = ['DKNode_NoOp', 'DKNode_DataMapper', 'DKNode_Action', 'DKNode_Container', 'DKNode_Ingredient']
    NODE_ACTION_TYPE_LIST = [
        'DKDataSource_DB2SQL',
        'DKDataSource_Dictionary',
        'DKDataSource_Container',
        'DKDataSource_NoOp',
        'DKDataSource_FTP',
        'DKDataSource_MSSQL',
        'DKDataSource_MYSQL',
        'DKDataSource_OrderRunInfo',
        'DKDataSource_PostgreSQL',
        'DKDataSource_S3',
        'DKDataSource_Salesforce',
        'DKDataSource_SFTP',
        'DKDataSource_SFTP_DSS',
        'DKDataSource_SHELL'
    ]
    DATASINK_TYPE_LIST = [
        'DKDataSink_DB2SQL',
        'DKDataSink_Dictionary',
        'DKDataSink_Container',
        'DKDataSink_NoOp',
        'DKDataSink_FTP',
        'DKDataSink_MSSQL',
        'DKDataSink_MYSQL',
        'DKDataSink_PostgreSQL',
        'DKDataSink_S3',
        'DKDataSink_Salesforce',
        'DKDataSink_SFTP',
        'DKDataSink_SFTP_DSS',
        'DKDataSink_SHELL'
    ]

    CONTAINER_NOTEBOOK_KEY_LIST = [
        'image-repo',
        'dockerhub-namespace',
        'dockerhub-username',
        'dockerhub-password'
    ]

    DATAMAPPER_NOTEBOOK_KEY_LIST = [
        'mappings'
    ]

    TEST_ACTION_TYPE_LIST = ['log', 'warning', 'stop-on-error']

    ERROR = 'error'
    WARNING = 'warning'

    def __init__(self, cfg):
        self.cfg = cfg
        pass

    def check_recipe(self, full_path):
        if self.cfg.get_skip_recipe_checker():
            return

        if full_path is None:
            error_message = 'Recipe path is None'
            self._display_error(error_message, DKCLIRecipeChecker.ERROR, full_path)

        self._check_main_files(full_path)
        self._recipe_check(full_path)
        self._check_nodes(full_path)

    def _check_main_files(self, full_path):
        main_files = ['description.json', 'graph.json', 'variations.json', 'variables.json']

        for file_name in main_files:
            if not os.path.isfile(os.path.join(full_path, file_name)):
                error_message = 'File is not present in recipe root path'
                self._display_error(error_message, DKCLIRecipeChecker.ERROR, os.path.join(full_path, file_name))

    def _recipe_check(self, full_path):
        for dir_name, subdir_list, file_list in os.walk(full_path):
            for file_name in file_list:
                if file_name not in IGNORED_FILES:
                    file_full_path = os.path.join(dir_name, file_name)
                    file_contents = self._get_file(file_full_path)
                    if file_contents is not None:
                        self._check_merge_issues(file_full_path, file_contents)
                        is_json, json_dict = self._check_json_format(file_full_path, file_contents)

    def _get_file(self, full_path):
        if DKFileEncode.is_binary(full_path):
            return None
        return DKFileHelper.read_file(full_path)

    def _check_merge_issues(self, full_path, file_contents):
        search_items = list()
        search_items.append(DKCLIRecipeChecker.MERGE_ISSUE_YOURS)
        search_items.append(DKCLIRecipeChecker.MERGE_ISSUE_THEIR)

        for item in search_items:
            if item in file_contents:
                error_message = 'File has merge conflicts. "%s" string found' % item
                self._display_error(error_message, DKCLIRecipeChecker.ERROR, full_path)

    def _check_json_format(self, full_path, file_contents):
        file_extension = DKFileEncode.get_file_extension(full_path)
        if 'json' != file_extension:
            return False, None
        try:
            json_dict = json.loads(file_contents)
        except Exception as e:
            error_message = 'File has an invalid json format. Error: %s' % str(e)
            self._display_error(error_message, DKCLIRecipeChecker.ERROR, full_path)
        return True, json_dict

    def _check_nodes(self, full_recipe_path):
        not_a_node_list = IGNORED_FILES
        not_a_node_list.append('resources')
        nodes = [name for name in os.listdir(full_recipe_path)
                 if os.path.isdir(os.path.join(full_recipe_path, name)) and name not in not_a_node_list]
        for node in nodes:
            node_path = os.path.join(full_recipe_path, node)
            DKCLIRecipeChecker._check_node(self, node_path)

    def _check_node(self, node_path):
        # Node needs a description.json
        description_json_path = os.path.join(node_path, 'description.json')
        if not os.path.isfile(description_json_path):
            self._display_error('No description.json in node.', DKCLIRecipeChecker.ERROR, description_json_path)

        # Check node description is not empty
        description_json_contents = self._get_file(description_json_path)
        if description_json_contents is None:
            self._display_error('description.json is empty.', DKCLIRecipeChecker.ERROR, description_json_path)

        # Check node type
        is_json, description_json_dict = self._check_json_format(description_json_path, description_json_contents)

        if 'type' not in description_json_dict:
            self._display_error('description.json has no "type" key.', DKCLIRecipeChecker.ERROR, description_json_path)

        if description_json_dict['type'] not in DKCLIRecipeChecker.NODE_TYPE_LIST:
            error_message = 'Bad node type: "%s". Needs to be one of this: %s' % (description_json_dict['type'], DKCLIRecipeChecker.NODE_TYPE_LIST)
            self._display_error(error_message, DKCLIRecipeChecker.ERROR, description_json_path)

        # check description
        if 'description' not in description_json_dict:
            self._display_error('description.json has no "description" key.', DKCLIRecipeChecker.WARNING, description_json_path)

        if 'description' in description_json_dict and not description_json_dict['description']:
            self._display_error('description.json has an empty "description" key.', DKCLIRecipeChecker.ERROR, description_json_path)
            self._display_error(error_message, DKCLIRecipeChecker.ERROR, description_json_path)

        # call specific checker for the node type
        node_method_name = '_check_node_' + str(description_json_dict['type'])
        node_method = getattr(self, node_method_name)
        node_method(node_path)

    def _check_node_DKNode_NoOp(self, node_path):
        pass

    def _check_node_DKNode_DataMapper(self, node_path):
        notebook_json_path = self._check_notebook_json_presence(node_path)
        self._check_json_dict_integrity('notebook.json', notebook_json_path, DKCLIRecipeChecker.DATAMAPPER_NOTEBOOK_KEY_LIST)

        folder_path = os.path.join(node_path, 'data_sinks')
        self._check_action(folder_path, check='datasinks')

        folder_path = os.path.join(node_path, 'data_sources')
        self._check_action(folder_path)

    def _check_node_DKNode_Action(self, node_path):
        # Check actions folder
        actions_path = os.path.join(node_path, 'actions')
        if not os.path.exists(actions_path):
            self._display_error('Node has no "actions" folder.', DKCLIRecipeChecker.ERROR, actions_path)

        self._check_action(actions_path)

    def _check_action(self, actions_path, check='datasources'):
        # check the folder exist
        if not os.path.exists(actions_path):
            self._display_error('Path does not exist.', DKCLIRecipeChecker.ERROR, actions_path)

        # Check json file inside the folder
        json_files = [name for name in os.listdir(actions_path)
                      if os.path.isfile(os.path.join(actions_path, name)) and name.endswith('.json')]

        if len(json_files) == 0:
            self._display_error('No .json file in folder', DKCLIRecipeChecker.ERROR, actions_path)

        # Check action type
        action_json_file_name = json_files[0]
        action_json_file_path = os.path.join(actions_path, action_json_file_name)
        file_contents = self._get_file(action_json_file_path)
        if file_contents is None:
            self._display_error('json file is empty', DKCLIRecipeChecker.ERROR, action_json_file_path)
        is_json, json_dict = self._check_json_format(action_json_file_path, file_contents)

        if check == 'datasources':
            expected_values = DKCLIRecipeChecker.NODE_ACTION_TYPE_LIST
        else:
            expected_values = DKCLIRecipeChecker.DATASINK_TYPE_LIST
        self._check_dict_key('type', json_dict, action_json_file_path, expected_values=expected_values)
        if 'wildcard' not in json_dict:
            self._check_dict_key('keys', json_dict, action_json_file_path)
        self._check_dict_key('tests', json_dict, action_json_file_path, error_severity=DKCLIRecipeChecker.WARNING)

        # check tests action types
        if 'tests' in json_dict:
            for test_key, test_value in json_dict['tests'].iteritems():
                if 'action' in test_value and test_value['action'] not in DKCLIRecipeChecker.TEST_ACTION_TYPE_LIST:
                    error_message = 'In "tests", "%s", "action". ' % test_key
                    error_message += 'Bad value "%s", needs to be one of this list: %s' % (test_value['action'], DKCLIRecipeChecker.TEST_ACTION_TYPE_LIST)
                    self._display_error(error_message, DKCLIRecipeChecker.ERROR, action_json_file_path)

    def _check_node_DKNode_Container(self, node_path):
        notebook_json_path = self._check_notebook_json_presence(node_path)
        self._check_json_dict_integrity('notebook.json', notebook_json_path, DKCLIRecipeChecker.CONTAINER_NOTEBOOK_KEY_LIST)

    def _check_node_DKNode_Ingredient(self, node_path):
        notebook_json_path = self._check_notebook_json_presence(node_path)

    def _check_dict_key(self, the_key, the_dict, file_path, check_presence=True, check_emptyness=False, error_severity='error', expected_values=None):
        if check_presence and the_key not in the_dict:
            self._display_error('json file with no "%s"' % the_key, error_severity, file_path)

        if check_emptyness and not the_dict[the_key]:
            self._display_error('json file with empty "%s"' % the_key, error_severity, file_path)

        if expected_values is not None and the_dict[the_key] not in expected_values:
            error_message = 'Bad value "%s", needs to be one of this list: %s' % (the_dict[the_key], expected_values)
            self._display_error(error_message, error_severity, file_path)

    def _check_notebook_json_presence(self, node_path):
        notebook_json_path = os.path.join(node_path, 'notebook.json')
        if not os.path.isfile(notebook_json_path):
            error_message = 'File notebook.json is missing'
            self._display_error(error_message, DKCLIRecipeChecker.ERROR, notebook_json_path)
        return notebook_json_path

    def _check_json_dict_integrity(self, file_name, file_path, items):
        file_contents = self._get_file(file_path)
        if file_contents is None:
            self._display_error('%s is empty' % file_name, DKCLIRecipeChecker.ERROR, file_path)
        is_json, json_dict = self._check_json_format(file_path, file_contents)
        for item in items:
            if item not in json_dict:
                error_message = 'Mandatory key "%s" is missing' % item
                self._display_error(error_message, DKCLIRecipeChecker.ERROR, file_path)

    def _display_error(self, message, severity, file_path):
        formatted_message = '%s---- %s%s' % (os.linesep, DKCLIRecipeChecker.EXCEPTION_MESSAGE_HEADER, os.linesep)
        formatted_message += '- Severity: %s%s' % (severity, os.linesep)
        formatted_message += '- File: %s%s' % (file_path, os.linesep)
        formatted_message += '- Message: %s%s' % (message, os.linesep)
        if DKCLIRecipeChecker.ERROR == severity:
            raise Exception(formatted_message)
        else:
            click.secho(formatted_message, fg='yellow')
