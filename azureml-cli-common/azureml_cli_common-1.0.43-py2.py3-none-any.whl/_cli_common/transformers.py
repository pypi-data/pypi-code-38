# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dateutil import parser
from collections import OrderedDict
from azureml._cli_common.constants import TABLE_OUTPUT_TIME_FORMAT
from azureml._model_management._constants import AKS_WEBSERVICE_TYPE, ACI_WEBSERVICE_TYPE


# MLC transforms
def transform_mlc_resource(result_tuple):
    result, verbose = result_tuple

    if result is None:
        return result

    if verbose:
        return result

    to_print = {
        'name': result['name'],
        'provisioningState': result['properties']['provisioningState'],
        'location': result['location'],
        'provisioningErrors': result['properties']['provisioningErrors']
    }

    return to_print


def table_transform_mlc_resource(result):
    return OrderedDict([
        ('name', result['name']),
        ('provisioningState', result['provisioningState']),
        ('location', result['location'])
    ])


def transform_mlc_resource_list(result_tuple):
    result_list, verbose = result_tuple

    return [transform_mlc_resource((obj, verbose)) for obj in result_list]


def table_transform_mlc_resource_list(result):
    return [
        OrderedDict([
            ('name', resource['name']),
            ('provisioningState', resource['provisioningState']),
        ])
        for resource in result]


def transform_mlc_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'id': result['id']
    }


def table_transform_mlc_delete(result):
    return OrderedDict([
        ('id', result['id'])
    ])


def transform_mlc_get_creds(result_tuple):
    result, verbose = result_tuple

    # Not using verbose, as result is already relatively minimal json. Including for consistency and future use.
    return result


def table_transform_mlc_get_creds(result):
    # The JSON is too long to reasonably display in a table.
    raise NotImplementedError()


# Model result transforms
def transform_model_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'framework': result['framework'],
        'frameworkVersion': result['frameworkVersion'],
        'createdTime': result['createdTime'],
        'tags': result['tags'] if result['tags'] else '',
        'properties': result['properties'] if result['properties'] else '',
        'description': result['description'] or '',
        'experimentName': result['experimentName'] or '',
        'runId': result['runId'] or ''
    }


def table_transform_model_show(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('framework', result['framework']),
                        ('frameworkVersion', result['frameworkVersion']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('tags', result['tags'] if result['tags'] else ''),
                        ('properties', result['properties'] if result['properties'] else ''),
                        ('experimentName', result['experimentName'] or ''),
                        ('runId', result['runId'] or '')])


def transform_model_list(result_tuple):
    result_list, verb = result_tuple

    if verb:
        return result_list

    return [
        {
            'name': result['name'],
            'id': result['id'],
            'version': result['version'],
            'framework': result['framework'],
            'frameworkVersion': result['frameworkVersion'],
            'createdTime': result['createdTime']
        }
        for result in result_list]


def table_transform_model_list(result_list):
    return [
        OrderedDict([('name', result['name']),
                     ('id', result['id']),
                     ('version', result['version']),
                     ('framework', result['framework']),
                     ('frameworkVersion', result['frameworkVersion']),
                     ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT))])
        for result in result_list]


def transform_model_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'id': result['id']
    }


def table_transform_model_delete(result):
    return OrderedDict([('id', result['id'])])


# Model package result transforms
def transform_model_package(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'createdTime': result['createdTime'],
        'creationState': result['creationState'],
        'description': result['description'] or '',
        'modelIds': result['modelIds'],
        'tags': result['tags'] if result['tags'] else ''
    }


def table_transform_model_package(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('creationState', result['creationState']),
                        ('modelIds', result['modelIds']),
                        ('tags', result['tags'])])


# Model profile transforms
def transform_model_profile(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return_dict = {
        'name': result['name'],
        'createdTime': result['createdTime'],
        'state': result['state'],
        'recommendedMemoryInGB': result['recommendedMemoryInGB'],
        'recommendedCpu': result["recommendedCpu"],
        'tags': result['tags'] if result['tags'] else ''
    }

    return return_dict


def table_transform_model_profile(result):
    return OrderedDict([('name', result['name']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('state', result['state']),
                        ('recommendedMemoryInGB', result['recommendedMemoryInGB']),
                        ('recommendedCpu', result['recommendedCpu']),
                        ('tags', result['tags'])])


# Image result transforms
def transform_image_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'createdTime': result['createdTime'],
        'creationState': result['creationState'],
        'description': result['description'] or '',
        'modelIds': result['modelIds'],
        'tags': result['tags'] if result['tags'] else ''
    }


def table_transform_image_show(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('creationState', result['creationState']),
                        ('modelIds', result['modelIds']),
                        ('tags', result['tags'])])


# Service result transforms
def transform_service_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return_dict = {
        'name': result['name'],
        'imageId': result['imageId'],
        'updatedAt': result['updatedTime'],
        'computeType': result['computeType'],
        'scoringUri': result["scoringUri"],
        'state': result['state'],
        'tags': result['tags'] if result['tags'] else '',
        'properties': result['properties'] if result['properties'] else ''
    }

    if result['computeType'] == ACI_WEBSERVICE_TYPE or result['computeType'] == AKS_WEBSERVICE_TYPE:
        model_names_versions = []
        if result['imageDetails']['modelDetails']:
            model_names_versions = ['{} [Ver. {}]'.format(model['name'], model['version']) for model in
                                    result['imageDetails']['modelDetails']]
            model_names_versions = ', '.join(model_names_versions)
        return_dict.update({
            'runtimeType': result['imageDetails']['targetRuntime']['runtimeType'] if 'targetRuntime' in result['imageDetails'] else None,
            'modelDetails': model_names_versions
        })

    return return_dict


def table_transform_service_show(result):
    return OrderedDict([('name', result['name']),
                        ('imageId', result['imageId']),
                        ('updatedAt', _convert_time(result['updatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('state', result['state']),
                        ('computeType', result['computeType']),
                        ('scoringUri', result['scoringUri']),
                        ('tags', result['tags']),
                        ('properties', result['properties'])])


def transform_service_list(result_tuple):
    result_list, verbose = result_tuple

    if verbose:
        return result_list

    return [
        transform_service_show((result, verbose))
        for result in result_list]


def table_transform_service_list(result_list):
    return [
        OrderedDict([('name', result['name']),
                     ('updatedAt', _convert_time(result['updatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                     ('state', result['state']),
                     ('scoringUri', result['scoringUri'])])
        for result in result_list]


def transform_service_run(result_tuple):
    result, verbose = result_tuple

    # 1. We ignore the verbosity flag, as "service run" just has a single property right now. Keeping it here for
    #    consistency with the rest of the CLI, and in case future SDK responses have more fields
    # 2. The SDK already attempts to return a JSON object from run, so we will just pass that along
    return result


def table_transform_service_run(result):
    return OrderedDict([
        ('result', result)
    ])


def transform_service_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name']
    }


def table_transform_service_delete(result):
    return OrderedDict([
        ('name', result['name'])
    ])


def transform_service_keys(result_tuple):
    # Maintaining verbosity flag for consistency with rest of CLI, and in case of future additions
    result, verbose = result_tuple

    return result


def table_transform_service_keys(result):
    return OrderedDict([
        ('primaryKey', result['primaryKey']),
        ('secondaryKey', result['secondaryKey'])
    ])


def _convert_time(time_str):
    time_obj = parser.parse(time_str)
    time_obj = time_obj.replace(microsecond=0, tzinfo=None)
    return time_obj
