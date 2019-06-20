################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import INSTANCE_DETAILS_TYPE, FUNCTION_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, is_of_python_basic_type, meta_props_str_conv
from watson_machine_learning_client.metanames import FunctionMetaNames
import os
import json
from watson_machine_learning_client.wml_client_error import WMLClientError, UnexpectedType
from watson_machine_learning_client.wml_resource import WMLResource

_DEFAULT_LIST_LENGTH = 50


class Functions(WMLResource):
    """
    Store and manage your functions.
    """
    ConfigurationMetaNames = FunctionMetaNames()
    """MetaNames for python functions creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Functions._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Functions._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, function, meta_props):
        """
            Create a function.

            As a 'function' may be used one of the following:
             - filepath to gz file
             - 'score' function reference, where the function is the function which will be deployed
             - generator function, which takes no argument or arguments which all have primitive python default values and as result return 'score' function

           **Parameters**

           .. important::
                #. **meta_props**:  meta data or name of the function. To see available meta names use **client.functions.ConfigurationMetaNames.get()**\n
                   **type**: str or dict\n
                #. **function**:  path to file with archived function content or function (as described above)\n
                   **type**: str or function\n

           **Output**

           .. important::
                **returns**: stored function metadata\n
                **return type**: dict\n

           **Example**

            The most simple use is (using `score` function):

            >>> def score(payload):
            >>>      values = [[row[0]*row[1]] for row in payload['values']]
            >>>      return {'fields': ['multiplication'], 'values': values}
            >>> stored_function_details = client.functions.store(score, name)

            Other, more interesting example is using generator function.
            In this situation it is possible to pass some variables:

                >>> wml_creds = {...}
                >>> def gen_function(wml_credentials=wml_creds, x=2):
                        def f(payload):
                            values = [[row[0]*row[1]*x] for row in payload['values']]
                            return {'fields': ['multiplication'], 'values': values}
                        return f
                >>> stored_function_details = client.functions.store(gen_function, name)

            In more complicated cases you should create proper metadata, similar to this one:

                >>> metadata = {
                >>>    client.repository.FunctionMetaNames.NAME: "function",
                >>>    client.repository.FunctionMetaNames.DESCRIPTION: "This is ai function",
                >>>    client.repository.FunctionMetaNames.RUNTIME_UID: "53dc4cf1-252f-424b-b52d-5cdd9814987f",
                >>>    client.repository.FunctionMetaNames.INPUT_DATA_SCHEMAS: [{"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]}],
                >>>    client.repository.FunctionMetaNames.OUTPUT_DATA_SCHEMAS:[{"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]}],
                >>>    client.repository.FunctionMetaNames.TAGS: [{"value": "ProjectA", "description": "Functions created for ProjectA"}]
                >>> }
                >>> stored_function_details = client.functions.store(score, metadata)
            """

        function = str_type_conv(function)
        import types
        Functions._validate_type(function, u'function', [STR_TYPE, types.FunctionType], True)
        meta_props = str_type_conv(meta_props)  # meta_props may be str, in this situation for py2 it will be converted to unicode
        Functions._validate_type(meta_props, u'meta_props', [dict, STR_TYPE], True)

        if type(meta_props) is STR_TYPE:
            meta_props = {
                self.ConfigurationMetaNames.NAME: meta_props
            }

        self.ConfigurationMetaNames._validate(meta_props)

        if type(function) is STR_TYPE:
            content_path = function
        else:
            try:
                import inspect
                import gzip
                import uuid
                import re
                import shutil
                code = inspect.getsource(function).split('\n')
                r = re.compile(r"^ *")
                m = r.search(code[0])
                intend = m.group(0)

                code = [line.replace(intend, '', 1) for line in code]

                args_spec = inspect.getargspec(function)

                defaults = args_spec.defaults if args_spec.defaults is not None else []
                args = args_spec.args if args_spec.args is not None else []

                if function.__name__ is 'score':
                    code = '\n'.join(code)
                    file_content = code
                elif len(args) == len(defaults):
                    for i, d in enumerate(defaults):
                        if not is_of_python_basic_type(d):
                            raise UnexpectedType(args[i], 'primitive python type', type(d))

                    new_header = 'def {}({}):'.format(
                        function.__name__,
                        ', '.join(
                            ['{}={}'.format(arg_name, json.dumps(default)) for arg_name, default in zip(args, defaults)]
                        )
                    )

                    code[0] = new_header
                    code = '\n'.join(code)
                    file_content = """
{}

score = {}()
""".format(code, function.__name__)
                else:
                    raise WMLClientError("Function passed is not \'score\' function nor generator function. Generator function should have no arguments or all arguments with primitive python default values.")

                tmp_uid = 'tmp_python_function_code_{}'.format(str(uuid.uuid4()).replace('-', '_'))
                filename = '{}.py'.format(tmp_uid)

                with open(filename, 'w') as f:
                    f.write(file_content)

                archive_name = '{}.py.gz'.format(tmp_uid)

                with open(filename, 'rb') as f_in:
                    with gzip.open(archive_name, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                os.remove(filename)

                content_path = archive_name
            except Exception as e:
                try:
                    os.remove(filename)
                except:
                    pass
                try:
                    os.remove(archive_name)
                except:
                    pass
                raise WMLClientError('Exception during getting function code.', e)

        try:
            if self.ConfigurationMetaNames.RUNTIME_UID not in meta_props:
                # print('No RUNTIME_UID passed. Creating default runtime... ', end="")
                # meta = {
                #     self._client.runtimes.ConfigurationMetaNames.NAME: meta_props[self.ConfigurationMetaNames.NAME] + "_py_3.5",
                #     self._client.runtimes.ConfigurationMetaNames.PLATFORM: {
                #         "name": "python",
                #         "version": "3,5"
                #     }
                # }
                # runtime_details = self._client.runtimes.store(meta)
                # runtime_uid = self._client.runtimes.get_uid(runtime_details)
                runtime_uid="ai-function_0.1-py3"
                print('Using default runtime with uid: {}'.format(runtime_uid))
                meta_props[self.ConfigurationMetaNames.RUNTIME_UID] = runtime_uid

            function_metadata = self.ConfigurationMetaNames._generate_resource_metadata(meta_props, with_validation=True,client=self._client)

            if not self._ICP:
                response_post = requests.post(self._href_definitions.get_functions_href(), json=function_metadata, headers=self._client._get_headers())
            else:
                response_post = requests.post(self._href_definitions.get_functions_href(), json=function_metadata, headers=self._client._get_headers(), verify=False)

            details = self._handle_response(expected_status_code=201, operationName=u'saving function', response=response_post)
            ##TODO_V4 Take care of this since the latest swagger endpoint is not working
            function_content_url = self._href_definitions.get_function_href(details['metadata']['guid']) + "/content"

            put_header = self._client._get_headers(no_content_type=True)
            with open(content_path, 'rb') as data:
                if not self._ICP:
                    response_definition_put = requests.put(function_content_url, data=data, headers=put_header)
                else:
                    response_definition_put = requests.put(function_content_url, data=data, headers=put_header, verify=False)

        except Exception as e:
            raise e
        finally:
            try:
                os.remove(archive_name)
            except:
                pass


        self._handle_response(200, u'saving function content', response_definition_put,json_response=False)

        return details

    def update(self, function_uid, changes):
        """
        Updates existing function metadata.

        **Parameters**

        .. important::
           #. **function_uid**:  UID of function which define what should be updated\n
              **type**: str\n
           #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
              **type**: dict\n

        **Output**

        .. important::
           **returns**: metadata of updated function\n
           **return type**: dict\n

        **Example**
         >>> metadata = {
         >>> client.functions.ConfigurationMetaNames.NAME:"updated_function"
         >>> }
         >>> function_details = client.functions.update(function_uid, changes=metadata)

        """
        function_uid = str_type_conv(function_uid)
        self._validate_type(function_uid, u'function_uid', STR_TYPE, True)
        self._validate_type(changes, u'changes', dict, True)
        meta_props_str_conv(changes)

        details = self.get_details(function_uid)

        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], changes,
                                                                            with_validation=True)

        url = self._href_definitions.get_function_href(function_uid)
        headers = self._client._get_headers()
        if not self._ICP:
            response = requests.patch(url, json=patch_payload, headers=headers)
        else:
            response = requests.patch(url, json=patch_payload, headers=headers, verify=False)
        updated_details = self._handle_response(200, u'function patch', response)

        return updated_details

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, function_uid, filename='downloaded_function.gz'):
        """
            Download function content from Watson Machine Learning repository to local file.

            **Parameters**

            .. important::
                #. **function_uid**:  stored function UID\n
                   **type**: str\n
                #. **filename**:  name of local file to create (optional) Example: function_content.gz\n
                   **default value**: downloaded_function.gz\n
                   **type**: str\n

            **Output**

            .. important::

               **returns**: Path to the downloaded function content\n
               **return type**: str\n

            .. note::
               If filename is not specified, the default filename is "downloaded_function.gz".\n

            **Example**

             >>> client.functions.download(function_uid, 'my_func.tar.gz')
        """
        if os.path.isfile(filename):
            raise WMLClientError(u'File with name: \'{}\' already exists.'.format(filename))

        artifact_uid = str_type_conv(function_uid)
        Functions._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)
        filename = str_type_conv(filename)
        Functions._validate_type(filename, u'filename', STR_TYPE, True)

        artifact_url = self._href_definitions.get_function_href(artifact_uid)
        artifact_content_url = self._href_definitions.get_function_latest_revision_content_href(artifact_uid)

        try:
            if not self._ICP:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True)
            else:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True, verify=False)
            self._handle_response(200, 'downloading function content', r, False)

            downloaded_model = r.content
            self._logger.info(u'Successfully downloaded artifact with artifact_url: {}'.format(artifact_url))
        except WMLClientError as e:
            raise e
        except Exception as e:
            raise WMLClientError(u'Downloading function content with artifact_url: \'{}\' failed.'.format(artifact_url), e)

        try:
            with open(filename, 'wb') as f:
                f.write(downloaded_model)
            print(u'Successfully saved function content to file: \'{}\''.format(filename))
            return os.getcwd() + "/"+filename
        except IOError as e:
            raise WMLClientError(u'Saving function content with artifact_url: \'{}\' failed.'.format(filename), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, function_uid):
        """
            Delete a stored function.

            **Parameters**

            .. important::
                #. **function_uid**:  stored function UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.functions.delete(function_uid)
        """
        function_uid = str_type_conv(function_uid)
        Functions._validate_type(function_uid, u'function_uid', STR_TYPE, True)
        ##TODO_V4 Uncomment this after deployments is ready
        # Delete associated deployments, so there will be no orphans
        deployments_details = filter(lambda x: function_uid in x['entity']['asset']['href'], self._client.deployments.get_details()['resources'])
        for deployment_detail in deployments_details:
           deployment_uid = self._client.deployments.get_uid(deployment_detail)
           print('Deleting orphaned function deployment \'{}\'... '.format(deployment_uid), end="")
           delete_status = self._client.deployments.delete(deployment_uid)
           print(delete_status)

        function_endpoint = self._href_definitions.get_function_href(function_uid)
        self._logger.debug(u'Deletion artifact function endpoint: {}'.format(function_endpoint))
        if not self._ICP:
            response_delete = requests.delete(function_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(function_endpoint, headers=self._client._get_headers(), verify=False)
        return self._handle_response(204, u'function deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, function_uid=None, limit=None):
        """
            Get metadata of function(s). If no function UID is specified all functions metadata is returned.

           **Parameters**

           .. important::
                #. **function_uid**:  UID of function (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: function(s) metadata\n
                **return type**: dict\n
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all functions metadata is fetched\n

           **Example**

             >>> function_details = client.functions.get_details(function_uid)
             >>> function_details = client.functions.get_details()
         """
        function_uid = str_type_conv(function_uid)
        Functions._validate_type(function_uid, u'function_uid', STR_TYPE, False)
        Functions._validate_type(limit, u'limit', int, False)

        url = self._href_definitions.get_functions_href()

        return self._get_artifact_details(url, function_uid, limit, 'functions')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(function_details):
        """
                Get UID of stored function.

                **Parameters**

                .. important::

                   #. **function_details**:  Metadata of the stored function\n
                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: UID of stored function\n
                    **return type**: str\n

                **Example**

                 >>> function_details = client.repository.get_function_detailsf(function_uid)
                 >>> function_uid = client.functions.get_uid(function_details)
        """
        Functions._validate_type(function_details, u'function_details', object, True)
        Functions._validate_type_of_details(function_details, FUNCTION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(function_details, u'function_details',
                                                           [u'metadata', u'guid'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(function_details):
        """
            Get url of stored function.

           **Parameters**

           .. important::
                #. **function_details**:  stored function details\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: href of stored function\n
                **return type**: str\n

           **Example**

             >>> function_details = client.repository.get_function_detailsf(function_uid)
             >>> function_url = client.functions.get_href(function_details)
        """
        Functions._validate_type(function_details, u'function_details', object, True)
        Functions._validate_type_of_details(function_details, FUNCTION_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(function_details, u'function_details', [u'metadata', u'href'])

    def list(self, limit=None):
        """
            List stored functions. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all functions in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.functions.list()
        """

        function_resources = self.get_details()[u'resources']
        function_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'],
                              m[u'entity'][u'type']) for m in function_resources]

        self._list(function_values, [u'GUID', u'NAME', u'CREATED', u'TYPE'], limit, _DEFAULT_LIST_LENGTH)