# coding=utf-8
from __future__ import print_function
import json
import time
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.utility_classes.utils import executeCommandWithResult, executeCommand

logger = FastpathLogger(__name__)

def getRCInstanceCredentials(instance_params):
    '''
    Returns the credentials for the instance of the service specified.
    If there is no instance available, a new one is provisioned. If there is no
    existing key, a new one is created.
    '''
    service_name = instance_params['service_name']
    instance_name = instance_params['instance_name']
    service_plan_name = instance_params['service_plan_name']
    service_region = instance_params['service_region']
    key_name = instance_params['key_name']
    key_role = instance_params['key_role']

    logger.log_info('\tLooking for existing instances of service "{}"'.format(service_name))
    metadataMapList = getRCServiceInstanceMetadata(service_name, True)
    metadataMap = {}
    if metadataMapList is not None:
        for metadataMap in metadataMapList:
            logger.log_info('\tFound existing instance "{}" of "{}"'.format(metadataMap['Name'], service_name))
        logger.log_info('\tUsing instance {}'.format(metadataMap['Name']))
        metadataMap = metadataMapList[0]
        instance_name = metadataMap['Name']
    else:
        logger.log_info('\tNo existing instance of "{}" found.'.format(service_name))
        logger.log_info('\tCreating a new instance "{}" for service "{}"'.format(instance_name, service_name))
        metadataMapList = createRCServiceInstance(instance_name, service_name, service_plan_name, service_region)
        metadataMap = metadataMapList[0]
        logger.log_info('\tCreated instance "{}" of "{}"'.format(metadataMap['Name'], service_name))

    logger.log_info('\tLooking for existing credentials with name "{}"'.format(key_name))
    credentials = getRCServiceKey(key_name)

    if credentials is None:
        logger.log_info('\tExisting credentials with name "{}" not found'.format(key_name))
        logger.log_info('\tGenerating credentials with name "{}"'.format(key_name))
        credentials = createRCServiceKey(key_name, key_role, instance_name)
        logger.log_info('\tGenerated "{}" for "{}"'.format(key_name, instance_name))
    else:
        logger.log_info('\tExisting credentials with name "{}" for instance "{}" found, reusing'.format(key_name, instance_name))
    return credentials[0]

def getRCServiceInstanceMetadata(name, is_service_name):
    '''
    If a service is specified, returns a map of metadata properties of all its instances else returns None
    If an instance is specidied, returns a map of its metadata properties
    '''
    cmd = '"{}"'.format(name)
    if is_service_name:
        cmd = '"service_name: {} AND type:resource-instance"'.format(name)
    cmd = 'bx resource search {}'.format(cmd)
    result = executeCommandWithResult(cmd)
    if (result is None or result == 'No resources found'):
        return None
    i = -1
    metadataMapList = []
    for line in result.splitlines():
        if line.strip():
            key, value = line.split(':', 1)
            if key == 'Name':
                metadataMapList.append({})
                i += 1
            metadataMapList[i][key] = value.strip()
    return metadataMapList

def createRCServiceInstance(instance_name, service_name, service_plan, service_region):
    '''
    Create a RC Service instance using the specified values
    '''
    cmd = 'bx resource service-instance-create "{}" "{}" "{}" "{}"'.format(instance_name, service_name, service_plan, service_region)
    executeCommand(cmd)
    metadataMapList = getRCServiceInstanceMetadata(instance_name, False)
    # If instance details are not retrievable, give some time to create the instance
    if metadataMapList is None:
        for _ in range(12):
            time.sleep(5)
            metadataMapList = getRCServiceInstanceMetadata(instance_name, False)
            if metadataMapList is not None:
                break
    return metadataMapList

def deleteRCServiceInstance(instance_name):
    '''
    Delete a RC Service with the specified name.
    '''
    getRCServiceInstanceMetadata(instance_name, False)
    cmd = 'bx resource service-instance-delete "{}" -f'.format(instance_name)
    executeCommand(cmd)

def createRCServiceKey(key_name, key_role, instance_name):
    '''
    Creates a service key with the specified name for the specified instance
    with the specified role
    '''
    cmd = 'bx resource service-key-create "{}" "{}" --instance-name "{}"'.format(key_name, key_role, instance_name)
    executeCommand(cmd)
    result = getRCServiceKey(key_name)
    if result is None:
        for _ in range(12):
            time.sleep(5)
            result = getRCServiceKey(instance_name, False)
            if result is not None:
                break
    return result

def deleteRCServiceKey(key_name):
    '''
    Deletes a service key with the specified name.
    '''
    cmd = 'bx resource service-key-delete "{}" -f'.format(key_name)
    executeCommand(cmd)

def getRCServiceKey(key_name):
    '''
    retrieves a service key if it exists
    '''
    cmd = 'bx resource service-key {} --output json'.format(key_name)
    result = executeCommandWithResult(cmd)
    if result is not None:
        return json.loads(result)
    return result
