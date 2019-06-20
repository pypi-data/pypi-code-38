################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

import requests
from watson_machine_learning_client.wml_client_error import MissingValue, WMLClientError, NoWMLCredentialsProvided, ApiRequestFailure, UnexpectedType, MissingMetaProp, ForbiddenActionForPlan
from watson_machine_learning_client.href_definitions import HrefDefinitions
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.utils import get_type_of_details, STR_TYPE, str_type_conv


class WMLResource:
    def __init__(self, name, client):
        self._logger = get_logger(name)
        self._name = name
        WMLResource._validate_type(client, u'client', object, True)
        if client.wml_credentials is None:
            raise NoWMLCredentialsProvided
        WMLResource._validate_type(client.wml_credentials, u'wml_credentials', dict, True)
        wml_token = str_type_conv(client.wml_token)
        WMLResource._validate_type(wml_token, u'wml_token', STR_TYPE, True)
        self._client = client
        self._ICP = client.ICP

        if not client.ICP:
            self._wml_credentials = client.wml_credentials
            self._href_definitions = HrefDefinitions(client.wml_credentials)
        else:
            self._wml_credentials = client.service_instance._wml_credentials
            self._href_definitions = HrefDefinitions(client.service_instance._wml_credentials)

    def _handle_response(self, expected_status_code, operationName, response, json_response=True):
        if "dele" in operationName:
            if response.status_code == expected_status_code:
                return "SUCCESS"
            else:
                print(response.text)
                return "FAILED"
        if response.status_code == expected_status_code:

            self._logger.info(u'Successfully finished {} for url: \'{}\''.format(operationName, response.url))
            self._logger.debug(u'Response({} {}): {}'.format(response.request.method, response.url, response.text))
            if json_response:
                try:
                    return response.json()
                except Exception as e:
                    raise WMLClientError(u'Failure during parsing json response: \'{}\''.format(response.text), e)
            else:
                return response.text
        else:
            raise ApiRequestFailure(u'Failure during {}.'.format(operationName), response)

    @staticmethod
    def _get_required_element_from_dict(el, root_path, path):
        WMLResource._validate_type(el, root_path, dict)
        WMLResource._validate_type(root_path, u'root_path', STR_TYPE)
        WMLResource._validate_type(path, u'path', list)

        if path.__len__() < 1:
            raise WMLClientError(u'Unexpected path length: {}'.format(path.__len__))

        try:
            new_el = el[path[0]]
            new_path = path[1:]
        except Exception as e:
            raise MissingValue(root_path + '.' + str(path[0]), e)

        if path.__len__() > 1:
            return WMLResource._get_required_element_from_dict(new_el, root_path + u'.' + path[0], new_path)
        else:
            if new_el is None:
                raise MissingValue(root_path + u'.' + str(path[0]))

            return new_el

    @staticmethod
    def _validate_type(el, el_name, expected_type, mandatory=True):
        if el_name is None:
            raise MissingValue(u'el_name')

        el_name = str_type_conv(el_name)
        if type(el_name) is not STR_TYPE:
            raise UnexpectedType(u'el_name', STR_TYPE, type(el_name))

        if expected_type is None:
            raise MissingValue(u'expected_type')

        if type(expected_type) is not type and type(expected_type) is not list:
            raise UnexpectedType('expected_type', 'type or list', type(expected_type))

        if type(mandatory) is not bool:
            raise UnexpectedType(u'mandatory', bool, type(mandatory))

        if mandatory and el is None:
            raise MissingValue(el_name)
        elif el is None:
            return

        if type(expected_type) is list:
            try:
                next((x for x in expected_type if isinstance(el, x)))
                return True
            except StopIteration:
                return False
        else:
            if not isinstance(el, expected_type):
                raise UnexpectedType(el_name, expected_type, type(el))

    @staticmethod
    def _validate_meta_prop(meta_props, name, expected_type, mandatory=True):
        if name in meta_props:
            WMLResource._validate_type(meta_props[name], u'meta_props.' + name, expected_type, mandatory)
        else:
            if mandatory:
                raise MissingMetaProp(name)

    @staticmethod
    def _validate_type_of_details(details, expected_type):
        actual_type = get_type_of_details(details)

        if type(expected_type) is list:
            expected_types = expected_type
        else:
            expected_types = [expected_type]

        if not any([actual_type == exp_type for exp_type in expected_types]):
            logger = get_logger(u'_validate_type_of_details')
            logger.debug(u'Unexpected type of \'{}\', expected: \'{}\', actual: \'{}\', occured for details: {}'.format(
                u'details', expected_type, actual_type, details))
            raise UnexpectedType(u'details', expected_type, actual_type)

    def _get_artifact_details(self, base_url, uid, limit, resource_name, summary=None,pre_defined=None):
        op_name = 'getting {} details'.format(resource_name)

        if uid is None:
            return self._get_with_or_without_limit(url=base_url, limit=limit, op_name=resource_name,summary=summary,pre_defined=pre_defined)
        else:
            # if not is_uid(uid):
            #     raise WMLClientError(u'Failure during {}, invalid uid: \'{}\''.format(op_name, uid)) # TODO

            url = base_url + u'/' + uid

            if not self._ICP:
                response_get = requests.get(
                    url,
                    headers=self._client._get_headers()
                )
            else:
                response_get = requests.get(
                    url,
                    headers=self._client._get_headers(),
                    verify=False
                )

            return self._handle_response(200, op_name, response_get)

    def _get_with_or_without_limit(self, url, limit, op_name,summary,pre_defined):
        params = {}
        if summary == "False":
            params.update({u'summary': u'false'})
        if pre_defined == "True":
            params.update({u'system_runtimes': u'true'})
        if limit is not None:
            if limit < 1:
                raise WMLClientError('Limit cannot be lower than 1.')
            elif limit > 1000:
                raise WMLClientError('Limit cannot be larger than 1000.')
            params.update({u'limit': limit})
        if len (params) > 0:
            if not self._ICP:
                response_get = requests.get(
                    url,
                    headers=self._client._get_headers(),
                    params=params
                )
            else:
                response_get = requests.get(
                    url,
                    headers=self._client._get_headers(),
                    params=params,
                    verify=False
                )

            return self._handle_response(200, op_name, response_get)
        else:

            resources = []

            while True:
                if not self._ICP:
                    response_get = requests.get(
                        url,
                        headers=self._client._get_headers()

                    )
                else:
                    response_get = requests.get(
                        url,
                        headers=self._client._get_headers(),
                        verify=False
                    )

                result = self._handle_response(200, op_name, response_get)
                resources.extend(result['resources'])

                if 'next' not in result:
                    break
                else:

                    url = self._wml_credentials["url"]+result['next']['href']


            return {
                "resources": resources
            }

    def _list(self, values, header, limit, default_limit, sort_by='CREATED'):
        if sort_by is not None and sort_by in header:
            column_no = header.index(sort_by)
            values = sorted(values, key=lambda x: x[column_no], reverse=True)

        from tabulate import tabulate

        if limit is None:
            table = tabulate([header] + values[:default_limit])
            print(table)
            if len(values) > default_limit:
                print('Note: Only first {} records were displayed. To display more use \'limit\' parameter.'.format(default_limit))
        else:
            table = tabulate([header] + values)
            print(table)
